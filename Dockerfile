FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
COPY src/ ./src/
COPY app.py ./

# Accept GUARDRAILS_API_KEY as a build argument (passed from docker-compose)
ARG GUARDRAILS_API_KEY=""

RUN pip3 install -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Only configure guardrails if API key is provided (non-empty)
RUN if [ -n "$GUARDRAILS_API_KEY" ]; then yes | guardrails configure --token $GUARDRAILS_API_KEY; fi

RUN guardrails hub install hub://guardrails/toxic_language \
    && guardrails hub install hub://guardrails/profanity_free \
    && guardrails hub install hub://guardrails/reading_time \
    && guardrails hub install hub://guardrails/sensitive_topics \
    && guardrails hub install hub://guardrails/valid_length

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]