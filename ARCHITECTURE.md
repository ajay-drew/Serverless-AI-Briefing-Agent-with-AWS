# Serverless AI Agent Briefing System - Architecture & Implementation Plan

## Project Overview
A cloud-native AI agent that autonomously searches, filters, and summarizes custom news using LangGraph workflows. TLDR-style personalized briefings delivered via email at user-scheduled times. Deployed entirely on AWS serverless infrastructure with zero infrastructure management.

## AI Agent Core Capabilities
1. **Autonomous Workflow**: LangGraph agent orchestrates search → deduplication → summarize → email pipeline
2. **Multi-Tool Integration**: Tavily (search), Groq LLM (reasoning/summarization), AWS SES (email), DynamoDB (storage), Calendar (scheduling)
3. **Per-User Scheduling**: Timezone-aware email delivery at personalized times via EventBridge
4. **Deduplication System**: Article-level and user-level duplicate prevention with database tracking
5. **State Management**: Agent maintains context, user preferences, and execution history across workflow steps

## Recommended Architecture: Serverless AI Agent on AWS

### Cloud Infrastructure Stack
- **Compute**: AWS Lambda (Containerized) - Hosts LangGraph agent runtime with Groq integration
- **Orchestration**: EventBridge - Per-user scheduled triggers with timezone support
- **API Layer**: Lambda Function URL - RESTful endpoints for agent queries and user management
- **Storage**: DynamoDB - Three tables: news_articles (deduplication), user_summaries (sent tracking), user_preferences (config)
- **Email**: SES - Personalized HTML email briefings with delivery tracking
- **Frontend**: S3 + CloudFront - React SPA with three dashboards: onboarding, metrics, query interface
- **Observability**: CloudWatch - Agent execution metrics, logs, and custom dashboards

### AI Agent Architecture
**LangGraph Workflow (8 Nodes)**:
1. **Calendar Check Node**: Timezone-aware time validation using Calendar Tool
2. **Query Analysis Node**: Groq LLM analyzes user preferences and generates search queries
3. **Search Node**: Tavily tool executes multiple searches based on user topics
4. **Deduplication Node**: Database Tool checks article hashes and user history to prevent repeats
5. **Summarize Node**: Groq LLM generates unique 1-2 line summaries ensuring no repetition
6. **Store Node**: Database Tool saves articles and marks as sent to user
7. **Format Node**: Template-based email formatting with personalization
8. **Email Node**: SES Tool sends personalized briefing to user

### Tool Integration
- **Email Tool**: AWS SES integration for sending personalized HTML emails with delivery status tracking
- **Calendar Tool**: Timezone-aware datetime operations using pytz, validates send times per user
- **Database Tool**: DynamoDB operations for deduplication (article hashes), user tracking (sent summaries), preferences storage

### Frontend Structure
- **Single URL Application**: React SPA with tab-based navigation
- **Dashboard 1 - User Onboarding**: Email input, timezone selection, topic preferences, schedule time, form validation
- **Dashboard 2 - Metrics Dashboard**: Articles processed, duplicates prevented, emails sent, user engagement, cost metrics, real-time charts
- **Dashboard 3 - Query Interface**: Custom search input, results display, query history, manual briefing trigger

### Error Handling & Resilience
- **Retry Logic**: Exponential backoff for API failures (Groq, Tavily, SES)
- **Graceful Degradation**: Fallback to cached results if search fails, skip user if email fails
- **Rate Limit Handling**: Queue management for API rate limits with exponential backoff
- **API Quota Enforcement**: Daily counters in DynamoDB track Tavily usage, reject requests when limits reached (18/day email, 20/day real-time, 980/month total)
- **Error Notifications**: CloudWatch alarms for critical failures, email notifications for admin
- **Transaction Safety**: DynamoDB conditional writes prevent duplicate processing

### Metrics & Monitoring
- **Real-Time Metrics**: Articles processed per day, duplicates prevented count, email success rate, user engagement
- **Cost Tracking**: Cost per email, API usage costs, Lambda execution costs
- **Performance Metrics**: Average processing time, email delivery latency, deduplication efficiency
- **CloudWatch Dashboards**: Custom dashboards for agent health, user activity, cost analysis

### User Onboarding Flow
- **Registration Form**: Email validation, timezone dropdown, topic checkboxes, time picker
- **Preference Storage**: Saves to DynamoDB user_preferences table with TTL
- **EventBridge Setup**: Creates per-user scheduled rule for email delivery
- **Confirmation Email**: Welcome email with preferences summary and unsubscribe link

### Documentation
- **API Documentation**: OpenAPI/Swagger specs for all endpoints, request/response examples
- **Architecture Diagrams**: System design, data flow, workflow diagrams
- **Setup Guide**: Step-by-step deployment instructions, environment variables, AWS setup
- **User Guide**: How to subscribe, manage preferences, understand metrics
- **Developer Guide**: Code structure, adding new tools, extending workflow

## Data Flow
**Scheduled Path**: EventBridge (per-user cron) → Lambda Agent → Calendar Check → Query Analysis → Search → Deduplication → Summarize → Store → Format → Email (SES) → User
**Interactive Path**: React UI → Lambda Function URL → Query Analysis → Search → Deduplication → Summarize → JSON Response → UI Display
**Onboarding Path**: React Form → Lambda Function URL → Validation → DynamoDB Write → EventBridge Rule Creation → Confirmation Email

## Implementation Timeline
- **Day 1-2**: LangGraph agent setup, workflow definition, tool integration (Tavily, Groq, Database, Email, Calendar)
- **Day 3**: AWS Lambda containerization, EventBridge per-user scheduler, DynamoDB schema design
- **Day 4**: Deduplication logic, error handling, retry mechanisms, CloudWatch logging
- **Day 5**: React frontend with three dashboards (onboarding, metrics, query), Lambda Function URL
- **Day 6**: SES integration, email templates, user onboarding flow, end-to-end testing
- **Day 7**: Metrics dashboard implementation, CloudWatch custom dashboards, comprehensive documentation

## API Rate Limiting & Capacity Planning

### Tavily API Limits (Enforced)
- **Email Briefings**: Maximum 18 searches per day (540/month)
- **Real-Time Queries**: Maximum 20 searches per day (600/month)
- **Total Cap**: 980 searches per month (enforced to prevent overage)
- **Implementation**: Daily counter with DynamoDB tracking, reject requests when limit reached

### Maximum User Capacity (Free Tier)

**Calculation Based on Constraints:**
- **Email Briefings**: 18 searches/day ÷ 1.5 searches per briefing = **12 users maximum**
- **Assumption**: Each user briefing uses ~1.5 Tavily searches (multiple topics combined)
- **Real-Time Queries**: 20 searches/day available for on-demand queries (shared across all users)

**AWS Free Tier Capacity:**
- **Lambda**: 1M requests/month → Supports ~33,000 briefings/month (well above 12 users × 30 days = 360)
- **SES**: 62,000 emails/month → Supports 2,066 users (well above 12 users)
- **DynamoDB**: 25 GB storage, 200M requests/month → Supports thousands of users
- **EventBridge**: 14M custom events/month → Supports thousands of scheduled rules
- **S3/CloudFront**: 5 GB storage, 1 TB transfer → Supports hundreds of users

**Bottleneck**: Tavily API limit (18 searches/day) = **12 users maximum** for email briefings

### Capacity Summary
- **Maximum Users (Email Briefings)**: 12 users (limited by Tavily API: 18 searches/day)
- **Real-Time Query Capacity**: 20 searches/day (shared across all users)
- **AWS Services**: All well within free tier limits for 12 users
- **Monthly Tavily Usage**: ~960 searches/month (540 email + 420 real-time, capped at 980)

## Cost Estimate
**AWS Services**: $0.00/month (all within free tier for 12 users)
- Lambda: Free (1M requests, 400K GB-seconds)
- SES: Free (62,000 emails/month)
- DynamoDB: Free (25 GB, 200M requests)
- EventBridge: Free (14M events/month)
- S3/CloudFront: Free (5 GB, 1 TB transfer)

**External APIs**:
- **Groq**: $0.00-$5.00/month (free tier covers ~12 users)
- **Tavily**: $1.00-$5.00/month (980 searches/month)

**Total Monthly Cost**: $1.00-$10.00/month for up to 12 users

## Key Technologies
**AI Agent**: LangGraph, Groq LLM (Llama 3/Mixtral), Tavily API
**Tools**: AWS SES, DynamoDB, Calendar (pytz), Database (boto3)
**Cloud**: AWS Lambda, EventBridge, SES, DynamoDB, S3, CloudFront, CloudWatch
**Frontend**: React, TypeScript, Chart.js (metrics visualization)
