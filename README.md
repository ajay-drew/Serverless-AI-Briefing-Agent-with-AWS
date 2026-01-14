# Serverless AI Briefing Agent with AWS

A cloud-native AI agent that autonomously searches, filters, and summarizes custom news using LangGraph workflows. TLDR-style personalized briefings delivered via email at user-scheduled times.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## Features

- **Autonomous Workflow**: LangGraph agent orchestrates search → deduplication → summarize → email pipeline
- **Multi-Tool Integration**: Tavily (search), Groq LLM (reasoning/summarization), AWS SES (email), DynamoDB (storage), Calendar (scheduling)
- **Per-User Scheduling**: Timezone-aware email delivery at personalized times
- **Deduplication System**: Article-level and user-level duplicate prevention
- **State Management**: Agent maintains context, user preferences, and execution history

## Setup

### Prerequisites

- Python 3.9+
- API keys for:
  - Groq API (https://console.groq.com/)
  - Tavily API (https://tavily.com/)
  - AWS credentials (for Day 3+ deployment)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Serverless-AI-Briefing-Agent-with-AWS
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your API keys
# Required: GROQ_API_KEY, TAVILY_API_KEY
# Optional (for Day 3+): AWS credentials
```

### Environment Variables

Create a `.env` file with the following variables:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-70b-versatile
TAVILY_API_KEY=your_tavily_api_key_here
AWS_ACCESS_KEY_ID=your_aws_access_key_id_here  # For Day 3+
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key_here  # For Day 3+
AWS_REGION=us-east-1
```

## Usage

### Quick Start - Run Agent

**Windows:**
```bash
run_agent.bat
```

**Linux/Mac:**
```bash
chmod +x run_agent.sh
./run_agent.sh
```

This will:
- Create virtual environment (if needed)
- Install dependencies
- Check for .env file
- Run the agent

### Running Tests

**Windows:**
```bash
test_day1-2.bat
```

**Linux/Mac:**
```bash
chmod +x test_day1-2.sh
./test_day1-2.sh
```

### Manual Run

Run the agent:

```bash
python main.py
```

Or use the command file:

```bash
run.bat
```

### Sending Test Emails

Send a test email using the EmailTool:

```bash
send_email.bat
```

Or run directly:

```bash
python send_email.py
```

**Custom Email:**
```bash
python send_email.py "Subject" "<html>Content</html>" recipient@example.com
```

**Configuration:**
- Add `TEST_EMAIL_RECIPIENT=your-email@example.com` to your `.env` file
- Add `SES_FROM_EMAIL=noreply@yourdomain.com` to your `.env` file
- For real email sending, configure AWS SES credentials in `.env`
- **Mock Mode**: Emails are automatically saved to `temp/emails/` folder (no AWS required for testing)
  - Files saved as: `email_YYYYMMDD_HHMMSS_recipient_subject.eml` and `.html`
  - Open `.html` files in a browser to preview emails
  - Open `.eml` files in any email client (Outlook, Thunderbird, etc.)

### Running Tests

The project includes a comprehensive pytest test suite with unit, integration, and end-to-end tests.

**Run all tests:**

**Windows:**
```bash
run_tests.bat
```

**Linux/Mac:**
```bash
chmod +x run_tests.sh
./run_tests.sh
```

**Run specific test categories:**
```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# End-to-end tests only
pytest tests/e2e/ -v

# Run with coverage report
pytest tests/ --cov=agent --cov-report=html
```

**Test Structure:**
- `tests/unit/` - Unit tests for individual tools and components
- `tests/integration/` - Integration tests for tool interactions and workflow nodes
- `tests/e2e/` - End-to-end tests for complete workflow execution

### Using the Agent Programmatically

```python
from agent import create_agent
from agent.state import AgentState

# Create agent
app = create_agent()

# Define initial state
initial_state: AgentState = {
    "user_email": "user@example.com",
    "user_preferences": {
        "topics": ["AI", "technology"],
        "timezone": "America/New_York",
        "schedule_time": "09:00",
    },
    "search_queries": [],
    "articles": [],
    "deduplicated_articles": [],
    "summaries": [],
    "email_content": "",
    "errors": [],
    "metadata": {},
}

# Run workflow
final_state = app.invoke(initial_state)
```

## Workflow

The LangGraph workflow consists of 8 nodes:

1. **Calendar Check**: Validates if it's time to send (timezone-aware)
2. **Query Analysis**: Generates search queries from user preferences (Groq LLM)
3. **Search**: Executes Tavily searches for news articles
4. **Deduplication**: Filters duplicates (article-level and user-level)
5. **Summarize**: Generates 1-2 line summaries (Groq LLM)
6. **Store**: Saves articles to database
7. **Format**: Formats email content (Groq LLM)
8. **Email**: Sends personalized briefing (mock in Day 1-2, real SES in Day 6)

## Tools

### Tavily Tool
- Searches news articles using Tavily API
- Returns articles with title, URL, content, published date, and relevance score
- Includes retry logic with exponential backoff

### Groq Tool
- **analyze_preferences()**: Generates search queries from user topics
- **summarize_article()**: Creates 1-2 line summaries
- **generate_email_content()**: Formats HTML email content

### Database Tool
- **Day 1-2**: In-memory mock implementation
- **Day 3+**: Real DynamoDB integration
- Functions: check_article_hash(), check_user_history(), store_article(), mark_sent_to_user()

### Email Tool
- **Real AWS SES Integration**: Automatically uses AWS SES if credentials are configured
- **Mock Mode**: Saves emails to `temp/emails/` folder using Python's built-in `email` library
- **Features**:
  - `send_email()`: Send HTML emails with automatic text fallback
  - `draft_email()`: Prepare email content without sending
  - Reads recipient from `TEST_EMAIL_RECIPIENT` in `.env`
  - Supports both HTML and plain text content
  - **Mock Mode**: Saves emails as both `.eml` (standard email format) and `.html` (for preview) files
  - Files are saved with timestamp and sanitized filenames in `temp/emails/` directory

### Calendar Tool
- Timezone-aware datetime operations using pytz
- Validates send times with configurable tolerance window
- Supports all standard timezones (e.g., "America/New_York", "Europe/London")

## Project Structure

```
/
├── agent/
│   ├── __init__.py          # Package initialization
│   ├── workflow.py           # LangGraph workflow definition
│   ├── state.py              # State management and schemas
│   └── tools/
│       ├── __init__.py
│       ├── tavily_tool.py    # Tavily search integration
│       ├── groq_tool.py      # Groq LLM integration
│       ├── database_tool.py  # DynamoDB operations (mock for Day 1-2)
│       ├── email_tool.py     # AWS SES integration (mock for Day 1-2)
│       └── calendar_tool.py  # Timezone-aware scheduling
├── config.py                 # Environment variable loading
├── requirements.txt          # Python dependencies
├── pytest.ini                # Pytest configuration
├── test_agent.py             # Simple test script
├── run_tests.bat             # Windows test runner
├── run_tests.sh              # Linux/Mac test runner
├── tests/                    # Pytest test suite
│   ├── conftest.py           # Shared fixtures
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── e2e/                  # End-to-end tests
├── .env.example              # Environment variable template
└── README.md                 # This file
```

## Implementation Timeline

- **Day 1-2**: ✅ LangGraph agent setup, workflow definition, tool integration (COMPLETED)
- **Day 3**: AWS Lambda containerization, EventBridge per-user scheduler, DynamoDB schema design
- **Day 4**: Deduplication logic, error handling, retry mechanisms, CloudWatch logging
- **Day 5**: React frontend with three dashboards, Lambda Function URL
- **Day 6**: SES integration, email templates, user onboarding flow, end-to-end testing
- **Day 7**: Metrics dashboard implementation, CloudWatch custom dashboards, comprehensive documentation

## Development Notes

- **Day 1-2**: Database and Email tools use mock implementations for local testing
- All tools include basic error handling and retry logic
- Workflow is designed to be testable locally before AWS deployment
- State management uses TypedDict for type safety

## License

See [LICENSE](LICENSE) file for details.
