# Usage Examples & Tutorials

## Quick Start

### Installation
```bash
pip install portfolio-system-sdk
```

### Basic Usage
```python
from portfolio_system import PortfolioSystem

# Initialize
ps = PortfolioSystem(api_key="your-api-key")

# Get a profile
profile = ps.profiles.get("romanchaa997")
print(f"Name: {profile.name}")
print(f"Skills: {profile.skills}")
```

## Example 1: Search for Developers

### Finding Python ML Engineers
```python
results = ps.search.hybrid(
    query="Python machine learning engineer with 5+ years experience",
    filters={
        "location": "Remote",
        "min_experience_years": 5
    },
    limit=10
)

for result in results:
    print(f"Username: {result.username}")
    print(f"Match Score: {result.similarity_score:.2%}")
    print(f"Matching Skills: {result.matching_skills}")
    print("---")
```

## Example 2: Analyze a Profile

```python
# Get detailed profile analysis
profile = ps.profiles.get("romanchaa997")

print(f"GitHub: {profile.github_url}")
print(f"Location: {profile.location}")
print(f"\nTop Skills:")
for skill in profile.top_skills[:5]:
    print(f"  - {skill.name}: {skill.proficiency}/10")

print(f"\nProjects:")
for project in profile.projects:
    print(f"  - {project.name}: {project.description[:50]}...")
```

## Example 3: Generate Recommendations

```python
# Get job recommendations for a profile
user_id = "romanchaa997"
recs = ps.recommendations.get(
    user_id=user_id,
    type="opportunities",
    limit=5
)

for rec in recs:
    print(f"Title: {rec.title}")
    print(f"Match Score: {rec.match_score:.2%}")
    print(f"Reason: {rec.reason}")
    print(f"URL: {rec.url}")
    print("---")
```

## Example 4: Create Custom Embeddings

```python
# Generate embedding for custom text
text = "Expert in building scalable ML systems and distributed computing"
embedding = ps.embeddings.generate(
    text=text,
    model="sentence-transformers/all-mpnet-base-v2"
)

print(f"Embedding dimension: {len(embedding)}")
print(f"First 5 values: {embedding[:5]}")

# Find similar profiles
similar = ps.embeddings.find_similar(
    embedding=embedding,
    limit=5
)

for profile in similar:
    print(f"{profile.username}: {profile.similarity_score:.2%}")
```

## Example 5: Batch Processing

```python
import asyncio
from portfolio_system import PortfolioSystem

async def process_profiles():
    async with PortfolioSystem(api_key="key") as ps:
        usernames = ["user1", "user2", "user3", "user4", "user5"]
        
        # Fetch all profiles concurrently
        profiles = await asyncio.gather(
            *[ps.profiles.get_async(u) for u in usernames]
        )
        
        for profile in profiles:
            print(f"Processing {profile.username}...")
            # Process each profile

# Run
asyncio.run(process_profiles())
```

## Example 6: Advanced Search with Custom Weights

```python
# Customize search weights
results = ps.search.hybrid(
    query="DevOps engineer Kubernetes Docker",
    filters={"location": "San Francisco"},
    weights={
        "semantic_similarity": 0.4,      # 40% semantic match
        "skill_match": 0.35,             # 35% exact skill match
        "project_relevance": 0.15,       # 15% project relevance
        "experience_recency": 0.1        # 10% recent experience
    },
    limit=20
)
```

## Example 7: Monitor API Usage

```python
# Check API quota and usage
usage = ps.get_usage_stats()

print(f"Requests this hour: {usage.requests_this_hour}")
print(f"Requests this month: {usage.requests_this_month}")
print(f"Quota: {usage.monthly_quota}")
print(f"Remaining: {usage.remaining_quota}")
```

## Example 8: Webhook Integration

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook/profile-updated', methods=['POST'])
def handle_profile_update():
    data = request.json
    
    user_id = data['user_id']
    updated_fields = data['updated_fields']
    
    print(f"Profile {user_id} updated: {updated_fields}")
    
    # Regenerate embeddings for updated profile
    ps.embeddings.regenerate(user_id)
    
    return {"status": "processed"}

if __name__ == '__main__':
    app.run(port=5000)
```

## Example 9: Export Profile Data

```python
import json
import csv

# Export as JSON
profile = ps.profiles.get("romanchaa997")
with open("profile.json", "w") as f:
    json.dump(profile.to_dict(), f, indent=2)

# Export skills as CSV
with open("skills.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(["Skill", "Proficiency", "Years"])
    for skill in profile.skills:
        writer.writerow([skill.name, skill.proficiency, skill.years_experience])
```

## Example 10: Real-time Profile Updates with WebSocket

```python
import asyncio
from portfolio_system import PortfolioSystem

async def watch_profile_updates():
    ps = PortfolioSystem(api_key="your-key")
    
    async with ps.websocket() as ws:
        # Subscribe to updates for specific user
        await ws.subscribe(
            event_type="profile_updated",
            user_id="romanchaa997"
        )
        
        # Listen for updates
        async for event in ws:
            if event.type == "profile_updated":
                print(f"Profile updated: {event.changes}")
            elif event.type == "skill_added":
                print(f"New skill: {event.skill}")
            elif event.type == "project_added":
                print(f"New project: {event.project.name}")

asyncio.run(watch_profile_updates())
```

## Common Patterns

### Error Handling
```python
from portfolio_system.exceptions import (
    NotFoundError,
    AuthenticationError,
    RateLimitError
)

try:
    profile = ps.profiles.get("nonexistent")
except NotFoundError:
    print("Profile not found")
except RateLimitError:
    print("Rate limited, retry later")
except AuthenticationError:
    print("Invalid API key")
```

### Pagination
```python
page = 1
while True:
    results = ps.profiles.list(page=page, limit=50)
    if not results:
        break
    
    for profile in results:
        process_profile(profile)
    
    page += 1
```

### Caching
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_profile_cached(username):
    return ps.profiles.get(username)

# First call: fetches from API
profile1 = get_profile_cached("user1")

# Second call: returns cached result
profile2 = get_profile_cached("user1")
```

## Troubleshooting

### Connection Issues
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('portfolio_system').setLevel(logging.DEBUG)

ps = PortfolioSystem(api_key="key")  # Debug logs will show
```

### Rate Limiting
```python
import time

def make_request_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError as e:
            wait_time = e.retry_after
            print(f"Rate limited, waiting {wait_time}s...")
            time.sleep(wait_time)
    raise Exception("Max retries exceeded")
```

## Performance Tips

1. Use batch operations when possible
2. Implement caching for frequently accessed data
3. Use connection pooling
4. Paginate large result sets
5. Use filters to reduce result size

## Support
For more examples and help, visit: https://docs.portfolio-system.com
