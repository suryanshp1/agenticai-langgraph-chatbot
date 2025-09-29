# Guardrails AI Integration

This guide explains how Guardrails AI is integrated into your LangGraph application to provide safety, validation, and quality control for LLM interactions.

## 🛡️ What is Guardrails AI?

Guardrails AI is a Python framework that adds safety rails to LLM applications by:
- Validating inputs and outputs
- Detecting toxic/harmful content
- Ensuring output quality and structure
- Preventing sensitive topic discussions
- Adding content moderation

## 🚀 Features Implemented

### 1. Input Validation
- **Toxic Language Detection**: Prevents harmful input from reaching the LLM
- **Profanity Filtering**: Blocks inappropriate language
- **Length Validation**: Ensures inputs are within reasonable limits (1-2000 chars)

### 2. Output Quality Control
- **Content Length**: Validates response length (10-5000 chars)
- **Reading Time**: Ensures responses are appropriately sized (1-300 seconds reading time)
- **Quality Assurance**: Maintains response quality standards

### 3. Content Moderation
- **Sensitive Topics**: Detects and prevents discussions of harmful topics
- **Safety Filtering**: Blocks violence, hate speech, harassment content
- **Threshold-based Detection**: Configurable sensitivity levels

### 4. Structured Output Validation
- **Schema Validation**: Ensures outputs match expected formats
- **Type Safety**: Validates data types and structures
- **Confidence Scoring**: Adds confidence metrics to responses

## 🔧 Configuration

### Environment Variables

```env
# Enable/disable Guardrails
GUARDRAILS_ENABLED=true

# Environment mode affects error display
STREAMLIT_ENV=development
```

### Guard Types

The application uses different guards for different scenarios:

1. **Input Safety Guard**: Validates user inputs
2. **Output Quality Guard**: Ensures response quality
3. **Content Moderation Guard**: Filters harmful content
4. **Structured Output Guard**: Validates response format

## 📋 Usage

### Automatic Protection

Guardrails are automatically applied to:
- All user inputs before processing
- All LLM outputs before display
- Tool interactions and responses
- MCP server communications

### Safety Warnings

When content is filtered, users see friendly warnings:
- 🛡️ **Input Safety**: Input was modified for safety
- 🛡️ **Output Safety**: Response was filtered for safety

### Fallback Behavior

If validation fails:
- **Input**: Safe alternative message is used
- **Output**: Filtered safe response is provided
- **Errors**: Application continues without breaking

## 🎯 Use Case Specific Guards

### Basic Chatbot
- Input safety validation
- Output quality control
- Basic content moderation

### Tool-Enabled Chatbots (MCP, Search)
- Enhanced content moderation
- Tool output validation
- Structured response validation

### AI News
- News content appropriateness
- Source validation
- Information accuracy checks

## 🔍 Monitoring Integration

Guardrails works seamlessly with Langfuse monitoring:
- Validation events are logged
- Safety metrics are tracked
- Guard performance is monitored
- Compliance reports available

## 🛠️ Customization

### Adding Custom Guards

```python
from guardrails import Guard
from guardrails.validators import ValidLength

# Create custom guard
custom_guard = Guard().use(
    ValidLength(min=5, max=100),
    # Add more validators
)

# Add to configuration
guardrails_config.guards["custom"] = custom_guard
```

### Adjusting Thresholds

```python
# Modify sensitivity in guardrails_config.py
ToxicLanguage(threshold=0.8)  # Higher = less sensitive
SensitiveTopics(threshold=0.7)  # Lower = more sensitive
```

## 📊 Safety Dashboard

### Status Indicators
- 🛡️ **Guardrails: ON/OFF** - Shows protection status
- **Active Guards**: Number of active validation rules
- **Safety Metrics**: Validation statistics

### Real-time Feedback
- Input validation warnings
- Output filtering notifications
- Safety compliance indicators

## 🚨 Troubleshooting

### Guardrails Not Working

1. **Check Environment Variable**:
   ```bash
   echo $GUARDRAILS_ENABLED
   ```

2. **Verify Installation**:
   ```bash
   pip list | grep guardrails
   ```

3. **Check Logs**:
   - Look for Guardrails initialization messages
   - Check for validation warnings in UI

### Performance Issues

1. **Disable Specific Guards**:
   ```python
   # In guardrails_config.py
   # Comment out heavy validators
   ```

2. **Adjust Thresholds**:
   ```python
   # Increase thresholds for better performance
   ToxicLanguage(threshold=0.9)
   ```

### False Positives

1. **Review Validation Rules**:
   - Check sensitive topics list
   - Adjust toxicity thresholds
   - Modify content filters

2. **Whitelist Content**:
   ```python
   # Add exceptions for specific use cases
   ```

## 🔒 Security Benefits

### Input Protection
- Prevents prompt injection attacks
- Blocks malicious content
- Validates input formats

### Output Safety
- Ensures appropriate responses
- Prevents harmful content generation
- Maintains quality standards

### Compliance
- Meets safety guidelines
- Supports content policies
- Enables audit trails

## 📈 Performance Impact

### Minimal Overhead
- Lightweight validation
- Async processing where possible
- Fail-safe fallbacks

### Optimization
- Cached validation results
- Efficient rule processing
- Smart threshold management

## 🔗 Resources

- [Guardrails AI Documentation](https://docs.guardrailsai.com/)
- [Guardrails Hub](https://hub.guardrailsai.com/)
- [GitHub Repository](https://github.com/guardrails-ai/guardrails)
- [Community Examples](https://github.com/guardrails-ai/guardrails/tree/main/examples)

## 🆘 Support

For issues with Guardrails integration:
1. Check the troubleshooting section
2. Review environment configuration
3. Consult Guardrails documentation
4. Open an issue in the project repository