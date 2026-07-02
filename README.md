# LeadFlow AI - Lead Intelligence & AI Outreach Platform

A scalable SaaS application for discovering businesses, analyzing them with AI, and generating personalized outreach campaigns.

## Features

- **Lead Discovery**: Collect leads from Google Maps and websites
- **Website Crawling**: Extract emails, phone numbers, social links, and technologies
- **AI Analysis**: Score leads, detect opportunities, and generate insights
- **Email Outreach**: Send personalized emails, track replies, and follow up
- **Dashboard**: Monitor pipeline progress and campaign performance
- **REST API**: Full API for integration with other tools

## Architecture

```
┌──────────────────────┐
│   FastAPI Backend    │
└──────────┬───────────┘
           │
┌──────────┼──────────────────────┐
│          │                      │
▼          ▼                      ▼
Job Manager   Workflow Engine   Dashboard API
    │              │
    └──────┬───────┘
           ▼
   Pipeline Orchestrator
           │
┌──────────┼─────────────┐
▼          ▼             ▼
Lead     Website       AI
Collector Crawler    Intelligence
    │          │          │
    └────┬─────┘          │
         ▼                ▼
  Lead Enrichment → Opportunity Detection
                      │
                      ▼
               Personalized Outreach
                      │
                      ▼
               PostgreSQL Database
```

## Tech Stack

### Backend
- **Python 3.12+**
- **FastAPI** - Modern async web framework
- **SQLAlchemy 2** - Async ORM
- **Alembic** - Database migrations
- **PostgreSQL** - Primary database
- **Playwright** - Browser automation
- **BeautifulSoup4** - HTML parsing

### AI
- **OpenRouter API** - Unified AI provider interface
- **Modular AI Provider** - Swap providers (OpenAI, Claude, Gemini, Local Llama)
- **Prompt Templates** - Structured prompts for analysis
- **AI Scoring Engine** - Lead qualification

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Vite** - Build tool
- **React Query** - Data fetching
- **Recharts** - Charts

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local development)
- PostgreSQL 16+ (for local development)

### Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/your-org/leadflow-ai.git
cd leadflow-ai
```

2. Create `.env` file:
```bash
cp .env.example .env
```

3. Update `.env` with your settings:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/leadflow
OPENROUTER_API_KEY=your-openrouter-api-key
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

4. Start the application:
```bash
docker-compose up -d
```

5. Access the application:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000

### Local Development

1. Install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

2. Set up PostgreSQL and create database:
```sql
CREATE DATABASE leadflow;
```

3. Run migrations:
```bash
alembic upgrade head
```

4. Start the server:
```bash
uvicorn app.main:app --reload
```

5. Start the frontend:
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
leadflow-ai/
├── app/
│   ├── api/
│   │   ├── routes/          # API endpoints
│   │   ├── middleware/       # Custom middleware
│   │   └── dependencies.py  # FastAPI dependencies
│   ├── core/
│   │   ├── config.py        # Configuration
│   │   ├── logger.py        # Logging setup
│   │   └── security.py      # Auth utilities
│   ├── database/
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── session.py        # DB session
│   │   ├── migrations/       # Alembic migrations
│   │   └── repository/       # Data access layer
│   ├── collectors/          # Lead collectors
│   │   ├── base.py
│   │   ├── google_maps/
│   │   └── websites/
│   ├── crawler/             # Website crawler
│   │   ├── crawler.py
│   │   ├── parser.py
│   │   ├── extractor.py
│   │   └── tech_detector.py
│   ├── ai/                  # AI layer
│   │   ├── analyzer.py
│   │   ├── providers/       # AI provider interface
│   │   └── templates/       # Prompt templates
│   ├── outreach/            # Email outreach
│   │   ├── providers/       # Email provider interface
│   │   ├── service.py
│   │   └── templates/
│   └── workflows/           # Pipeline orchestration
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom hooks
│   │   ├── api/             # API client
│   │   └── types/           # TypeScript types
│   └── ...
├── tests/                   # Test suite
├── docker/                  # Docker files
└── docker-compose.yml
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/logout` - Logout

### Workspaces
- `POST /api/v1/workspaces/` - Create workspace
- `GET /api/v1/workspaces/` - List workspaces
- `GET /api/v1/workspaces/{id}` - Get workspace
- `PATCH /api/v1/workspaces/{id}` - Update workspace
- `DELETE /api/v1/workspaces/{id}` - Delete workspace

### Leads
- `POST /api/v1/leads/` - Create lead
- `POST /api/v1/leads/bulk` - Bulk create leads
- `GET /api/v1/leads/` - List leads
- `GET /api/v1/leads/stats` - Get lead statistics
- `GET /api/v1/leads/search` - Search leads
- `GET /api/v1/leads/{id}` - Get lead details
- `PATCH /api/v1/leads/{id}` - Update lead
- `DELETE /api/v1/leads/{id}` - Delete lead

### Jobs
- `POST /api/v1/jobs/` - Create and start job
- `GET /api/v1/jobs/` - List jobs
- `GET /api/v1/jobs/{id}` - Get job status
- `POST /api/v1/jobs/{id}/cancel` - Cancel job

## Development

### Running Tests
```bash
# Unit tests
pytest tests/unit/ -v

# API tests
pytest tests/api/ -v

# All tests
pytest tests/ -v --cov=app
```

### Code Style
```bash
# Format code
black app/ frontend/src/
isort app/ frontend/src/

# Type checking
mypy app/
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Add leads table"

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Extending the Platform

### Adding a New Collector

1. Create a new collector class:
```python
# app/collectors/my_source/collector.py
from app.collectors.base import BaseCollector, CollectedLead

class MySourceCollector(BaseCollector):
    name = "my_source"
    source_type = "my_source"
    
    async def collect(self, query: str, **kwargs) -> List[CollectedLead]:
        # Implementation
        pass
```

2. Register the collector in the pipeline.

### Adding a New AI Provider

1. Implement the provider interface:
```python
# app/ai/providers/my_provider.py
from app.ai.providers.base import BaseAIProvider

class MyProvider(BaseAIProvider):
    name = "my_provider"
    
    async def generate(self, prompt: str, **kwargs) -> AIResponse:
        # Implementation
        pass
    
    async def chat(self, messages: List[Message], **kwargs) -> AIResponse:
        # Implementation
        pass
```

### Adding a New Email Provider

1. Implement the email provider interface:
```python
# app/outreach/providers/my_provider.py
from app.outreach.providers.base import BaseEmailProvider

class MyEmailProvider(BaseEmailProvider):
    name = "my_email"
    
    async def send(self, to_email: str, subject: str, body: str, **kwargs) -> EmailResult:
        # Implementation
        pass
```

## Deployment

### Docker Deployment

1. Build the image:
```bash
docker build -t leadflow-ai:latest -f docker/Dockerfile .
```

2. Run with Docker Compose:
```bash
docker-compose -f docker-compose.yml up -d
```

### Production Checklist

- [ ] Set secure `SECRET_KEY`
- [ ] Configure PostgreSQL with SSL
- [ ] Set up Redis for job queue
- [ ] Configure SMTP with TLS
- [ ] Set up AI provider API keys
- [ ] Enable HTTPS
- [ ] Set up monitoring/alerting
- [ ] Configure backups

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request
