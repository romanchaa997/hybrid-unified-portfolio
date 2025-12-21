# 🚀 Hybrid Unified Portfolio System - Setup & Installation Guide

## Quick Start (5 minutes)

### Prerequisites
- Python 3.10+
- pip (Python package manager)
- Git
- Virtual environment (recommended)

### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/romanchaa997/hybrid-unified-portfolio.git
cd hybrid-unified-portfolio

# 2. Create virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# 3. Install all dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configurations

# 5. Initialize database (if needed)
# python scripts/init_db.py

# 6. Run the application
python main.py
```

---

## Detailed Installation

### 1. Environment Setup

#### Step 1a: Clone Repository
```bash
git clone https://github.com/romanchaa997/hybrid-unified-portfolio.git
cd hybrid-unified-portfolio
```

#### Step 1b: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Using conda (alternative):**
```bash
conda create -n portfolio python=3.10
conda activate portfolio
```

### 2. Install Dependencies

#### Option A: Install All Dependencies (Recommended)
```bash
pip install -r requirements.txt
```

#### Option B: Install Core Dependencies Only
```bash
pip install fastapi==0.104.1
pip install uvicorn==0.24.0
pip install pydantic==2.5.0
pip install numpy==1.24.3
pip install pandas==2.1.3
pip install sentence-transformers==2.2.2
```

#### Option C: Install in Groups

**Core API Dependencies:**
```bash
pip install fastapi==0.104.1 uvicorn==0.24.0 pydantic==2.5.0
```

**AI/ML & Vector Processing:**
```bash
pip install openai==1.3.0 sentence-transformers==2.2.2 \
            pinecone-client==3.0.0 numpy==1.24.3 \
            scikit-learn==1.3.2
```

**Data Processing:**
```bash
pip install pandas==2.1.3 python-dotenv==1.0.0 pyyaml==6.0.1
```

**GitHub Integration:**
```bash
pip install PyGithub==2.1.1 requests==2.31.0
```

**Database:**
```bash
pip install sqlalchemy==2.0.23 psycopg2-binary==2.9.9
```

**Caching:**
```bash
pip install redis==5.0.1
```

**Development Tools:**
```bash
pip install black==23.12.0 flake8==6.1.0 mypy==1.7.1
```

**Testing:**
```bash
pip install pytest==7.4.3 pytest-asyncio==0.21.1 pytest-cov==4.1.0
```

### 3. Environment Variables Configuration

#### Copy Example Environment File
```bash
cp .env.example .env
```

#### Edit .env with Your Configuration
```bash
# .env file

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_ENV=development

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Pinecone Vector Database
PINCONE_API_KEY=your_pinecone_api_key_here
PINCONE_ENVIRONMENT=your_pinecone_env_here
PINCONE_INDEX=your_index_name_here

# GitHub Integration
GITHUB_TOKEN=your_github_personal_access_token_here
GITHUB_USERNAME=your_github_username_here

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/portfolio_db
DATABASE_ECHO=false

# Redis Cache
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### 4. Database Initialization

#### For PostgreSQL:
```bash
# Create database
creatdb hybrid_portfolio

# Or using psql:
psql -U postgres -c "CREATE DATABASE hybrid_portfolio;"

# Initialize tables
python -m alembic upgrade head
```

#### For SQLite (Development):
Update DATABASE_URL in .env:
```
DATABASE_URL=sqlite:///./portfolio.db
```

### 5. Verify Installation

```bash
# Check Python version
python --version  # Should be 3.10+

# Check pip packages
pip list | grep -E "fastapi|numpy|pandas|sentence-transformers"

# Test imports
python -c "import fastapi; import numpy; import pandas; print('All imports successful!')"

# Test embedding module
python -c "from src.embeddings import EmbeddingGenerator; print('Embeddings module loaded')"

# Test skill extraction module
python -c "from src.skill_extraction import SkillExtractor; print('Skill extraction module loaded')"

# Test semantic search module
python -c "from src.semantic_search import SemanticSearchEngine; print('Semantic search module loaded')"
```

---

## Docker Setup

### Using Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### Manual Docker Build

```bash
# Build image
docker build -t hybrid-portfolio .

# Run container
docker run -p 8000:8000 --env-file .env hybrid-portfolio
```

---

## Running the Application

### Development Server

```bash
# Run FastAPI development server
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# API will be available at: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Production Server

```bash
# Using Gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

# Or using Docker
docker run -p 8000:8000 --env-file .env hybrid-portfolio
```

---

## Testing the Installation

### Run Test Suite

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_embeddings.py

# Run with verbose output
pytest -v
```

### Quick Functionality Test

```python
# test_setup.py
from src.embeddings import EmbeddingGenerator, ProfileEmbedder
from src.skill_extraction import SkillExtractor
from src.semantic_search import SemanticSearchEngine

# Test 1: Embeddings
print("Testing Embeddings...")
gen = EmbeddingGenerator()
text_embedding = gen.encode(["Python developer with AI expertise"])
print(f"✓ Embedding shape: {text_embedding.shape}")

# Test 2: Skill Extraction
print("\nTesting Skill Extraction...")
extractor = SkillExtractor()
result = extractor.extract("I am proficient in Python, JavaScript, React, and AWS")
print(f"✓ Found skills: {result.all_skills}")

# Test 3: Semantic Search
print("\nTesting Semantic Search...")
engine = SemanticSearchEngine()
profile = {
    "summary": "Full-stack Python developer with machine learning expertise",
    "skills": ["Python", "FastAPI", "PyTorch", "Docker"]
}
engine.add_profile("user1", profile)
results = engine.search("machine learning engineer", top_k=5)
print(f"✓ Search returned {len(results)} results")

print("\n✅ All tests passed!")
```

Run the test:
```bash
python test_setup.py
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fastapi'"
**Solution:** Activate virtual environment and install requirements
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: "Port 8000 already in use"
**Solution:** Use a different port
```bash
uvicorn main:app --port 8001
```

### Issue: "PostgreSQL connection failed"
**Solution:** Check DATABASE_URL in .env and PostgreSQL service status
```bash
# Start PostgreSQL
sudo service postgresql start  # Linux
brew services start postgresql  # macOS

# Test connection
psql -U postgres -c "SELECT 1;"
```

### Issue: "OpenAI API key invalid"
**Solution:** Verify API key in .env file
```bash
# Update .env with correct key
echo "OPENAI_API_KEY=sk-..." >> .env
```

### Issue: "ImportError: cannot import name 'main' from partially initialized module"
**Solution:** Make sure you're not naming your test file 'main.py'
```bash
# Rename test files to avoid conflicts
mv main.py app.py  # if main.py is your test
```

---

## Package Dependencies Summary

### Core Framework (3 packages)
- fastapi==0.104.1 - Web framework
- uvicorn==0.24.0 - ASGI server
- pydantic==2.5.0 - Data validation

### AI/ML & Embeddings (5 packages)
- openai==1.3.0 - OpenAI API client
- sentence-transformers==2.2.2 - Embedding models
- pinecone-client==3.0.0 - Vector database
- numpy==1.24.3 - Numerical computing
- scikit-learn==1.3.2 - ML utilities

### Data Processing (3 packages)
- pandas==2.1.3 - Data manipulation
- python-dotenv==1.0.0 - Environment variables
- pyyaml==6.0.1 - YAML parsing

### Integration (2 packages)
- PyGithub==2.1.1 - GitHub API
- requests==2.31.0 - HTTP requests

### Database (2 packages)
- sqlalchemy==2.0.23 - ORM
- psycopg2-binary==2.9.9 - PostgreSQL adapter

### Caching (1 package)
- redis==5.0.1 - Redis client

### Async/Real-time (2 packages)
- aiohttp==3.9.1 - Async HTTP
- websockets==12.0 - WebSocket support

### Development & Testing (6 packages)
- pytest==7.4.3 - Testing framework
- pytest-asyncio==0.21.1 - Async test support
- pytest-cov==4.1.0 - Coverage reports
- black==23.12.0 - Code formatter
- flake8==6.1.0 - Linter
- mypy==1.7.1 - Type checker

### Deployment (3 packages)
- gunicorn==21.2.0 - WSGI server
- python-json-logger==2.0.7 - JSON logging
- prometheus-client==0.19.0 - Metrics

**Total: 34 packages**

---

## Next Steps

1. **Configure Services**: Update .env with your API keys
2. **Initialize Database**: Run migration scripts
3. **Start Application**: Run `python main.py`
4. **Access API Docs**: Open http://localhost:8000/docs
5. **Test Endpoints**: Use Swagger UI or curl
6. **Deploy**: Follow deployment guide in DEPLOYMENT.md

---

## Support

For issues or questions:
- 📖 Check [docs/](https://github.com/romanchaa997/hybrid-unified-portfolio/tree/main/docs)
- 🐛 Report bugs on [Issues](https://github.com/romanchaa997/hybrid-unified-portfolio/issues)
- 💬 Contact via [email](mailto:romanchaa997@gmail.com)

---

**Happy coding! 🎉**
