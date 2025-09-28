# Langfuse Monitoring Setup

This guide helps you set up Langfuse monitoring for your LangGraph application to track LLM responses, costs, and performance.

## 🚀 Quick Start

### 1. Start Langfuse Services

```bash
# Start Langfuse database and server
docker-compose up -d langfuse-db langfuse-server

# Or use the setup script
python setup_langfuse.py
```

### 2. Configure Langfuse

1. Open http://localhost:3000 in your browser
2. Create an account or sign in
3. Create a new project (or use the default one)
4. Go to **Settings** → **API Keys**
5. Copy the **Secret Key** and **Public Key**

### 3. Update Environment Variables

Add to your `.env` file:

```env
LANGFUSE_SECRET_KEY=sk-lf-your-secret-key-here
LANGFUSE_PUBLIC_KEY=pk-lf-your-public-key-here
LANGFUSE_HOST=http://localhost:3000
```

### 4. Start the Application

```bash
# Start all services including your app
docker-compose up --build

# Or start just your app if Langfuse is already running
docker-compose up langgraph-agenticai
```

## 📊 What Gets Monitored

- **LLM Requests & Responses**: All interactions with Groq models
- **Token Usage**: Input and output tokens for cost calculation
- **Response Times**: Latency metrics for performance monitoring
- **User Sessions**: Track user interactions across conversations
- **Tool Usage**: Monitor MCP and other tool executions
- **Error Tracking**: Capture and analyze failures

## 🎯 Features

### In-App Monitoring
- ✅ Real-time monitoring status in sidebar
- ✅ Direct link to Langfuse dashboard
- ✅ Session tracking across conversations
- ✅ Automatic cost tracking

### Langfuse Dashboard
- 📈 **Traces**: Detailed view of each conversation
- 💰 **Costs**: Token usage and cost breakdown
- ⚡ **Performance**: Response time analytics
- 🔍 **Search**: Find specific interactions
- 📊 **Analytics**: Usage patterns and trends

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LANGFUSE_SECRET_KEY` | Your Langfuse secret key | Required |
| `LANGFUSE_PUBLIC_KEY` | Your Langfuse public key | Required |
| `LANGFUSE_HOST` | Langfuse server URL | `http://localhost:3000` |
| `TELEMETRY_ENABLED` | Enable Langfuse telemetry | `true` |

### Docker Compose Services

- **langfuse-db**: PostgreSQL database for Langfuse
- **langfuse-server**: Langfuse web application
- **langgraph-agenticai**: Your main application

## 🛠️ Troubleshooting

### Langfuse Not Starting

```bash
# Check service logs
docker-compose logs langfuse-server
docker-compose logs langfuse-db

# Restart services
docker-compose restart langfuse-server langfuse-db
```

### Connection Issues

1. Verify environment variables are set correctly
2. Check that Langfuse is accessible at http://localhost:3000
3. Ensure API keys are valid and have proper permissions

### Monitoring Not Working

1. Check the sidebar for monitoring status
2. Verify Langfuse credentials in `.env` file
3. Look for error messages in the Streamlit app

## 📚 Advanced Usage

### Custom Traces

```python
from src.langgraphagenticai.monitoring.langfuse_integration import langfuse_manager

# Create custom trace
trace = langfuse_manager.create_trace(
    name="custom_operation",
    user_id="user123",
    session_id="session456"
)
```

### Cost Analysis

Access detailed cost breakdowns in the Langfuse dashboard:
1. Go to **Analytics** → **Usage**
2. Filter by model, user, or time period
3. Export data for further analysis

## 🔗 Useful Links

- [Langfuse Documentation](https://langfuse.com/docs)
- [Langfuse GitHub](https://github.com/langfuse/langfuse)
- [LangChain Integration](https://langfuse.com/docs/integrations/langchain)

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Docker Compose logs
3. Consult Langfuse documentation
4. Open an issue in the project repository