# API Reference

## Base URL
```
https://api.portfolio-system.com/v1
```

## Authentication
All API requests require an API key in the `Authorization` header:
```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### Profiles

#### Get Profile
```http
GET /profiles/{username}
```
Retrieve a professional profile by GitHub username.

**Parameters:**
- `username` (string, required): GitHub username

**Response:**
```json
{
  "id": "uuid",
  "username": "romanchaa997",
  "name": "Igor",
  "bio": "AI/ML Engineer & Web3 Developer",
  "location": "Ukraine",
  "avatar_url": "https://...",
  "embeddings": [...],
  "skills": [...],
  "projects": [...]
}
```

#### List Profiles
```http
GET /profiles
```
List all profiles.

**Query Parameters:**
- `limit` (integer, default: 10): Number of results
- `offset` (integer, default: 0): Pagination offset

### Skills

#### Search Skills
```http
GET /skills/search
```
Search for skills across all profiles.

**Query Parameters:**
- `query` (string, required): Skill search query
- `limit` (integer, default: 10): Results per page

**Response:**
```json
{
  "results": [
    {
      "name": "Python",
      "proficiency": 9.0,
      "count": 156,
      "embedding": [...]
    }
  ],
  "total": 156
}
```

#### Get Skill Details
```http
GET /skills/{skill_id}
```
Get detailed information about a specific skill.

### Search

#### Hybrid Search
```http
POST /search/hybrid
```
Perform hybrid semantic and structured search.

**Request Body:**
```json
{
  "query": "Python ML engineer with Web3 experience",
  "filters": {
    "location": "Remote",
    "min_experience_years": 3
  },
  "weights": {
    "semantic": 0.6,
    "skill_match": 0.2,
    "project_relevance": 0.2
  },
  "limit": 20
}
```

**Response:**
```json
{
  "results": [
    {
      "profile_id": "uuid",
      "username": "user1",
      "similarity_score": 0.92,
      "matching_skills": ["Python", "ML", "Web3"],
      "match_explanation": "Matches 3/3 primary skills..."
    }
  ],
  "total": 45
}
```

#### Semantic Search
```http
POST /search/semantic
```
Search using only vector embeddings.

**Request Body:**
```json
{
  "query": "experienced in building scalable ML systems",
  "limit": 10
}
```

### Embeddings

#### Generate Embedding
```http
POST /embeddings/generate
```
Generate an embedding for custom text.

**Request Body:**
```json
{
  "text": "Python expert with 10 years of ML experience",
  "model": "sentence-transformers/all-mpnet-base-v2"
}
```

**Response:**
```json
{
  "embedding": [0.123, -0.456, ...],
  "dimension": 768,
  "model_used": "sentence-transformers/all-mpnet-base-v2"
}
```

#### Find Similar
```http
POST /embeddings/similar
```
Find profiles similar to a given embedding.

**Request Body:**
```json
{
  "embedding": [0.123, -0.456, ...],
  "limit": 5
}
```

### Recommendations

#### Get Recommendations
```http
GET /recommendations/{user_id}
```
Get personalized recommendations for a user.

**Query Parameters:**
- `type` (string): "opportunities", "collaborators", "projects"
- `limit` (integer, default: 10)

**Response:**
```json
{
  "recommendations": [
    {
      "id": "uuid",
      "title": "Senior ML Engineer Role",
      "match_score": 0.88,
      "reason": "Your skills match this role's requirements"
    }
  ]
}
```

### Projects

#### Get Project Analysis
```http
GET /projects/{project_id}/analysis
```
Get detailed analysis of a project.

**Response:**
```json
{
  "id": "uuid",
  "name": "Audityzer",
  "description": "...",
  "skills_demonstrated": ["Python", "Security", "ML"],
  "complexity_score": 8.5,
  "embedding": [...]
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "invalid_request",
  "message": "Missing required parameter: query",
  "code": 400
}
```

### 401 Unauthorized
```json
{
  "error": "unauthorized",
  "message": "Invalid or missing API key",
  "code": 401
}
```

### 404 Not Found
```json
{
  "error": "not_found",
  "message": "Resource not found",
  "code": 404
}
```

### 429 Rate Limited
```json
{
  "error": "rate_limited",
  "message": "Too many requests. Limit: 1000/hour",
  "code": 429,
  "retry_after": 60
}
```

## Rate Limiting
- **Default**: 1000 requests/hour per API key
- **Premium**: 10000 requests/hour
- **Enterprise**: Custom limits

## Pagination
For list endpoints:
```http
GET /profiles?limit=10&offset=20
```

## WebSocket Events

### Subscribe to Profile Updates
```javascript
const ws = new WebSocket('wss://api.portfolio-system.com/ws');
ws.send(JSON.stringify({
  action: 'subscribe',
  type: 'profile_updates',
  profile_id: 'uuid'
}));
```

### Event Types
- `profile_updated`: Profile information changed
- `new_project`: New project added
- `skill_change`: Skill proficiency updated
- `recommendation_match`: New matching opportunity found

## Code Examples

### Python
```python
import requests

headers = {"Authorization": "Bearer your-api-key"}

# Search
response = requests.post(
    "https://api.portfolio-system.com/v1/search/hybrid",
    headers=headers,
    json={
        "query": "Python ML engineer",
        "limit": 10
    }
)
results = response.json()
```

### JavaScript
```javascript
const apiKey = 'your-api-key';

fetch('https://api.portfolio-system.com/v1/search/hybrid', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    query: 'Python ML engineer',
    limit: 10
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

## SDKs
- **Python**: `pip install portfolio-sdk`
- **JavaScript**: `npm install portfolio-sdk`
- **Go**: `go get github.com/portfolio-system/sdk-go`

## Support
For API support, contact: api-support@portfolio-system.com
