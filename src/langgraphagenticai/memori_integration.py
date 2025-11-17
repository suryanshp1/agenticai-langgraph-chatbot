"""
Lightweight Memori integration for the project.

This module initializes a Memori instance, creates a small memory-tool
compatible wrapper, and provides a helper to wrap existing LLMs so that
conversation context can be retrieved from persistent memory and stored
back after LLM responses. The goal is to reduce token usage by fetching
relevant memories (summaries / notes) instead of sending long histories.

This integration is intentionally conservative: all Memori calls are
protected by try/except so the app continues to work even if Memori
is not available or fails at runtime.

Usage:
    from src.langgraphagenticai.memori_integration import wrap_llm_with_memori
    llm = wrap_llm_with_memori(llm)

"""
from typing import Any, List, Optional
import os

try:
    from memori import Memori, create_memory_tool
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
except Exception:  # pragma: no cover - safe fallback when Memori not installed
    Memori = None
    create_memory_tool = None
    SystemMessage = None
    HumanMessage = None
    AIMessage = None


class MemoryDisabledException(Exception):
    pass


class MemoryLLMWrapper:
    """Wraps an LLM to consult Memori before generating and to record after.

    Behavior:
    - On invoke/_generate: extract a short query from the user input, ask
      Memori for relevant memories, and if found, prepend a SystemMessage
      describing the relevant memories.
    - After LLM call: try to record the user/AI pair back into Memori so
      later sessions can benefit.

    The wrapper is defensive — errors in memory lookup/storage are logged
    (printed) but do not prevent the LLM from running.
    """

    def __init__(self, llm: Any, memory_system: Any, memory_tool: Any):
        self.llm = llm
        self.memory_system = memory_system
        self.memory_tool = memory_tool

    def _prepend_memories(self, messages: List[Any], query: str) -> List[Any]:
        try:
            if not self.memory_tool:
                return messages

            # Query memori for relevant memories. Use a concise prompt so we
            # don't blow token usage while retrieving.
            result = None
            try:
                # memory_tool may expose execute(query=...) like the example
                result = self.memory_tool.execute(query=query)
            except Exception:
                # Fallback: try search attribute
                if hasattr(self.memory_tool, "search"):
                    result = self.memory_tool.search(query)

            if not result:
                return messages

            # Build a short system-level summary to help the LLM.
            summary_text = f"Relevant memories:\n{result}" if isinstance(result, str) else f"Relevant memories: {str(result)}"

            # If langchain message classes are available, create a SystemMessage
            if SystemMessage is not None:
                sys_msg = SystemMessage(content=summary_text)
                return [sys_msg] + messages

            # Otherwise, try to prepend a dict-style message or simple string.
            # Many LLMs accept a list of dict messages as [{"role":"system", "content":"..."}, ...]
            if isinstance(messages, list) and messages and isinstance(messages[0], dict):
                sys_dict = {"role": "system", "content": summary_text}
                return [sys_dict] + messages

            # As a last resort, insert the summary as the first element in messages
            return [summary_text] + messages

        except Exception as e:
            print(f"[Memori] memory lookup failed: {e}")
            return messages

    def _record_conversation(self, user_input: str, ai_output: str):
        try:
            if not self.memory_system:
                return

            # Try known record method from example
            if hasattr(self.memory_system, "record_conversation"):
                self.memory_system.record_conversation(user_input=user_input, ai_output=ai_output)
                return

            # Try generic store/ingest methods
            if hasattr(self.memory_system, "ingest"):
                self.memory_system.ingest({"user_input": user_input, "ai_output": ai_output})
                return

            if hasattr(self.memory_system, "record"):
                self.memory_system.record({"user_input": user_input, "ai_output": ai_output})
                return

        except Exception as e:
            print(f"[Memori] failed to record conversation: {e}")

    # Delegate attribute access
    def __getattr__(self, name: str):
        return getattr(self.llm, name)

    # Support invoke-style API used across the project
    def invoke(self, input_data: Any, config: Optional[Any] = None, **kwargs) -> Any:
        # Try to extract a short user query for memory lookup
        user_text = None
        try:
            if isinstance(input_data, str):
                user_text = input_data
            elif isinstance(input_data, list):
                # find last human message
                for msg in reversed(input_data):
                    if isinstance(msg, dict) and msg.get("role") in ("user", "human"):
                        user_text = msg.get("content")
                        break
                    if HumanMessage is not None and isinstance(msg, HumanMessage):
                        user_text = msg.content
                        break
            elif isinstance(input_data, dict):
                if "input" in input_data:
                    user_text = input_data["input"]
        except Exception:
            user_text = None

        # Prepend memories
        messages_for_llm = input_data
        try:
            if user_text and self.memory_tool:
                messages_for_llm = self._prepend_memories(input_data if input_data else [], user_text)
        except Exception:
            messages_for_llm = input_data

        # Call underlying LLM
        result = None
        try:
            result = self.llm.invoke(messages_for_llm, config=config, **kwargs)
        except Exception:
            # If the LLM does not accept invoke signature, try _generate or call directly
            try:
                result = self.llm._generate(messages_for_llm, **kwargs)
            except Exception as e:
                # As last resort, call underlying object directly
                result = getattr(self.llm, "__call__", lambda x: None)(messages_for_llm)

        # Attempt to record the conversation
        try:
            ai_text = None
            if isinstance(result, str):
                ai_text = result
            elif AIMessage is not None and isinstance(result, AIMessage):
                ai_text = result.content
            elif isinstance(result, dict) and result.get("content"):
                ai_text = result.get("content")
            elif hasattr(result, "generations"):
                # LangChain result-like object
                try:
                    gens = getattr(result, "generations")
                    if gens and len(gens) > 0:
                        first = gens[0]
                        # try nested message/content
                        ai_text = getattr(first, "text", None) or getattr(first, "message", None)
                        if hasattr(ai_text, "content"):
                            ai_text = ai_text.content
                except Exception:
                    ai_text = str(result)

            if user_text and ai_text:
                self._record_conversation(user_text, str(ai_text))
        except Exception:
            pass

        return result


def init_memori(database_connect: Optional[str] = None, namespace: str = "langgraphagenticai", conscious_ingest: bool = True, verbose: bool = False):
    """Initialize Memori and return (memory_system, memory_tool).

    If Memori is not available (not installed), returns (None, None).
    """
    if Memori is None or create_memory_tool is None:
        print("[Memori] memorisdk not installed; skipping memory initialization")
        return None, None

    try:
        db_connect = database_connect or f"sqlite:///{namespace}_memory.db"
        memory_system = Memori(
            database_connect=db_connect,
            conscious_ingest=conscious_ingest,
            verbose=verbose,
            namespace=namespace,
        )
        memory_system.enable()
        memory_tool = create_memory_tool(memory_system)
        print(f"[Memori] initialized with namespace={namespace} db={db_connect}")
        return memory_system, memory_tool
    except Exception as e:
        print(f"[Memori] failed to initialize Memori: {e}")
        return None, None


def wrap_llm_with_memori(llm: Any, *, database_connect: Optional[str] = None, namespace: str = "langgraphagenticai") -> Any:
    """Convenience wrapper: initialize Memori and wrap provided LLM.

    If Memori cannot be initialized, returns the original LLM unchanged.
    """
    memory_system, memory_tool = init_memori(database_connect=database_connect, namespace=namespace)
    if not memory_system:
        return llm

    return MemoryLLMWrapper(llm, memory_system, memory_tool)
