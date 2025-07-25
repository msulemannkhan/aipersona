# Cohere LLM Integration Documentation

## Overview

This document describes the integration of Cohere's LLM API to replace hardcoded keyword matching with intelligent AI-powered risk assessment and content filtering. The changes were made to enhance the accuracy and contextual understanding of user message analysis while maintaining robust fallback mechanisms.

## Changes Made

### 1. Configuration Updates

**File**: `backend/app/core/config.py`
- Added `COHERE_API_KEY` configuration parameter
- The API key is loaded from the `COHERE_API_KEY` environment variable in the root `.env` file

```python
# Cohere Configuration
COHERE_API_KEY: str | None = None
COHERE_CHAT_MODEL: str = "command-r-plus"
COHERE_EMBED_MODEL: str = "embed-english-v3.0"
```

### 2. New Cohere Service Implementation

**File**: `backend/app/services/cohere_service.py`
- Created a new service class `CohereService` for intelligent risk assessment
- Implements AI-powered analysis using Cohere's Command-R-Plus model
- Provides structured risk assessment with confidence scores
- Includes comprehensive fallback mechanisms for API failures

**Key Features**:
- **Risk Level Assessment**: Categorizes messages as low, medium, high, or critical
- **Category Detection**: Identifies specific risk categories (suicide, violence, self-harm, etc.)
- **Confidence Scoring**: Provides 0.0-1.0 confidence scores for assessments
- **Crisis Resources**: Automatically suggests appropriate crisis intervention resources
- **Fallback Safety**: Falls back to keyword-based analysis when API fails

**API Model Used**: `command-r-plus` (powerful and context-aware for risk assessment)

### 3. Risk Assessment Service Updates

**File**: `backend/app/services/risk_assessment_service.py`

**Changes**:
- Replaced hardcoded keyword lists with Cohere LLM integration
- Updated `assess_message_risk()` method to use AI-powered analysis
- Removed `_quick_risk_screening()` method (replaced with LLM analysis)
- Added `_get_crisis_resources_for_categories()` helper method
- Centralized crisis resources in the service class
- Enhanced logging with confidence scores

**Benefits**:
- More accurate risk detection based on context and intent
- Reduced false positives from keyword matching
- Better understanding of nuanced language and expressions
- Higher confidence in risk assessments

### 4. Content Filter Service Updates

**File**: `backend/app/services/content_filter_service.py`

**Changes**:
- Replaced hardcoded keyword lists with Cohere LLM integration
- Updated `analyze_content()` method to be async and use AI analysis
- Added `_fallback_analysis()` method for API failure scenarios
- Restructured keyword arrays into `fallback_keywords` dictionary
- Updated `is_safe_content()` method to handle async operations

**Benefits**:
- Intelligent content filtering based on context
- Better detection of inappropriate content
- Reduced false positives and negatives
- Graceful degradation when API is unavailable

### 5. API Route Updates

**File**: `backend/app/api/routes/chat.py`
- Updated content analysis call to handle async `analyze_content()` method
- Changed `content_analysis = content_filter.analyze_content(message_in.content)` to `content_analysis = await content_filter.analyze_content(message_in.content)`

## Architecture

### Risk Assessment Flow

1. **User Message** → **Cohere LLM Analysis** → **Risk Assessment**
2. **Fallback**: If Cohere API fails → **Keyword-based Analysis** → **Risk Assessment**
3. **Content Filter Integration**: Combines LLM analysis with content filtering
4. **Database Storage**: Saves assessment results with confidence scores

### Fallback Mechanism

The system implements a robust fallback strategy:

1. **Primary**: Cohere LLM analysis with contextual understanding
2. **Secondary**: Keyword-based analysis when API fails
3. **Safety**: Always errs on the side of caution for user safety

## Configuration

### Environment Variables

Add to your `.env` file:
```env
COHERE_API_KEY=your_cohere_api_key_here
COHERE_CHAT_MODEL=command-r-plus
COHERE_EMBED_MODEL=embed-english-v3.0
```

### Cohere API Settings

- **Model**: `command-r-plus`
- **Temperature**: 0.1 (low for consistent results)
- **Max Tokens**: 500
- **Timeout**: 30 seconds

## Risk Categories

The system detects the following risk categories:

1. **suicide** - Suicidal ideation, plans, or intent
2. **self_harm** - Self-injury, cutting, or other self-destructive behaviors
3. **violence** - Threats or plans to harm others, violent ideation
4. **substance_abuse** - Drug or alcohol abuse, addiction concerns
5. **abuse** - Domestic violence, child abuse, sexual abuse
6. **mental_health_crisis** - Severe depression, anxiety, psychosis, breakdown
7. **relationship_crisis** - Relationship problems, divorce, breakup distress
8. **financial_crisis** - Bankruptcy, debt, financial distress
9. **sexual_content** - Inappropriate sexual content, sexual abuse
10. **general_distress** - General emotional distress, stress, worry

## Risk Levels

- **LOW**: Normal conversation, no significant risk indicators
- **MEDIUM**: Concerning patterns, mild distress indicators, potential risk factors
- **HIGH**: Strong indicators of crisis, distress, harmful thoughts, or inappropriate content
- **CRITICAL**: Immediate suicide/self-harm intent, specific plans, imminent danger

## Crisis Resources

The system provides appropriate crisis resources based on detected risk categories:

- **National Suicide Prevention Lifeline**: 988
- **Crisis Text Line**: Text HOME to 741741
- **National Domestic Violence Hotline**: 1-800-799-7233
- **SAMHSA National Helpline**: 1-800-662-HELP (4357)
- **Emergency Services**: 911

## Error Handling

### Cohere API Errors
- **Network Issues**: Falls back to keyword analysis
- **Rate Limiting**: Graceful degradation with retry logic
- **Invalid API Key**: Logs error and uses fallback
- **Service Unavailable**: Continues with keyword-based analysis

### Fallback Analysis
- Maintains original keyword-based logic as a safety net
- Provides reasonable risk assessments even when AI service fails
- Logs all fallback scenarios for monitoring

## Testing

The integration includes comprehensive testing:

1. **Normal Messages**: Verifies low-risk detection
2. **Concerning Messages**: Tests medium/high-risk detection
3. **Critical Messages**: Validates critical risk detection
4. **Fallback Scenarios**: Tests behavior when API fails
5. **Content Filtering**: Verifies content analysis accuracy

## Performance Considerations

- **Response Time**: Cohere API calls add ~1-3 seconds to message processing
- **Rate Limits**: Cohere free tier has rate limitations
- **Fallback Speed**: Keyword analysis is instant when API fails
- **Concurrent Requests**: Service handles multiple simultaneous requests

## Monitoring and Logging

Enhanced logging includes:
- Confidence scores for all assessments
- API response times and errors
- Fallback scenario triggers
- Risk category detection details

## Security Considerations

- **API Key Protection**: Cohere API key stored securely in environment variables
- **Data Privacy**: User messages are sent to Cohere API (review privacy policy)
- **Fallback Safety**: System never fails open - always provides risk assessment
- **Error Logging**: Sensitive information is not logged

## Future Enhancements

Potential improvements:
1. **Fine-tuning**: Custom model training for better accuracy
2. **Caching**: Cache frequent assessment results
3. **Multiple Models**: A/B testing with different LLM models
4. **Real-time Learning**: Incorporate counselor feedback for model improvement
5. **Batch Processing**: Process multiple messages efficiently

## Troubleshooting

### Common Issues

1. **"Invalid API Key"**: Verify COHERE_API_KEY in environment variables
2. **"Rate Limit Exceeded"**: Check API usage limits and upgrade plan if needed
3. **Timeout Errors**: Check network connectivity and Cohere service status
4. **High Fallback Usage**: Monitor API quotas and rate limits

### Debugging

- Check application logs for Cohere API errors
- Verify environment variable configuration
- Test API key with curl commands
- Monitor fallback frequency for API issues

## Conclusion

The Cohere LLM integration significantly enhances the system's ability to understand and assess user messages contextually, while maintaining robust fallback mechanisms for reliability. The implementation preserves all existing functionality while adding intelligent AI-powered analysis capabilities.

The system now provides:
- More accurate risk detection
- Better contextual understanding
- Reduced false positives
- Enhanced user safety
- Reliable fallback mechanisms
- Comprehensive crisis resource recommendations

This integration represents a significant improvement in the system's ability to provide appropriate support and intervention for users in crisis while maintaining the safety and reliability of the original keyword-based approach. 