# Embedding Strategy & Implementation

## Overview

The Hybrid Unified Portfolio System uses advanced embedding techniques to create meaningful vector representations of professional profiles, skills, projects, and experiences. This document outlines the embedding strategy and implementation approaches.

## Embedding Model Selection

### Primary Models

#### OpenAI Ada (Recommended for Production)
- **Dimension**: 1536
- **Max Input**: 8,000 tokens
- **Cost**: ~$0.10 per 1M tokens
- **Performance**: Excellent for semantic similarity
- **Use Case**: Production systems with budget flexibility

```python
from openai import OpenAI

client = OpenAI(api_key="sk-...")
embedding = client.embeddings.create(
    input="Machine Learning Engineer with 5 years experience",
    model="text-embedding-ada-002"
)
```

#### Sentence Transformers (Open Source)
- **Models**: all-MiniLM-L6-v2, all-mpnet-base-v2
- **Dimension**: 384 or 768
- **Local**: No API calls required
- **Performance**: Excellent open-source alternative
- **Use Case**: Self-hosted or cost-conscious deployments

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode("Machine Learning Engineer")
```

#### LLaMA Embeddings (Latest)
- **Dimension**: 768-1024
- **Speed**: Fast inference
- **Cost**: Free (self-hosted)
- **Quality**: Competitive with commercial models
- **Use Case**: On-premises or edge deployments

## Skill Embedding Strategy

### Level 1: Direct Skill Embedding
Individual skills are converted to vectors independently:

```python
skills = [
    "Python",
    "Machine Learning",
    "Natural Language Processing",
    "PyTorch",
    "Kubernetes"
]

skill_vectors = [embedder.encode(skill) for skill in skills]
```

### Level 2: Context-Aware Skill Embedding
Skills are embedded with contextual information:

```python
contextual_skills = [
    "Python for AI/ML applications",
    "Machine Learning model development",
    "NLP for chatbot and sentiment analysis",
    "PyTorch deep learning framework",
    "Kubernetes container orchestration"
]

contextual_vectors = [embedder.encode(skill) for skill in contextual_skills]
```

### Level 3: Proficiency-Weighted Embedding
Skills are embedded with proficiency levels:

```python
skill_proficiency = {
    "Python": 9.0,
    "Machine Learning": 8.5,
    "Natural Language Processing": 8.0,
    "Kubernetes": 7.5,
    "Web3/Blockchain": 8.8
}

# Weighted embeddings
weighted_vectors = {}
for skill, proficiency in skill_proficiency.items():
    base_vector = embedder.encode(skill)
    weighted_vectors[skill] = (proficiency / 10.0) * base_vector
```

## Project Embedding

### Approach 1: Repository README Embedding
```python
def embed_project_from_readme(repo_url, embedder):
    readme_text = fetch_readme(repo_url)
    summary = summarize_text(readme_text, max_length=500)
    embedding = embedder.encode(summary)
    return embedding
```

### Approach 2: Multi-File Analysis
```python
def embed_project_comprehensive(repo_url, embedder):
    artifacts = {
        "readme": fetch_file(repo_url, "README.md"),
        "description": fetch_repo_description(repo_url),
        "languages": get_primary_languages(repo_url),
        "topics": get_repo_topics(repo_url)
    }
    
    combined_text = f"""
    Repository: {artifacts['description']}
    Languages: {', '.join(artifacts['languages'])}
    Topics: {', '.join(artifacts['topics'])}
    Overview: {artifacts['readme'][:1000]}
    """
    
    embedding = embedder.encode(combined_text)
    return embedding
```

### Approach 3: Code Snippet Embedding
```python
def embed_code_samples(repo_url, embedder):
    # Extract significant code snippets
    code_snippets = extract_meaningful_code(repo_url, max_snippets=5)
    
    # Create descriptions of code
    descriptions = [analyze_code_snippet(snippet) for snippet in code_snippets]
    
    # Embed descriptions
    embeddings = [embedder.encode(desc) for desc in descriptions]
    
    # Average the embeddings
    project_embedding = np.mean(embeddings, axis=0)
    return project_embedding
```

## Experience Vector Construction

### Temporal Dimension
```python
import math

def calculate_experience_factor(years, skill):
    # Base experience from years
    base = min(years, 10)  # Cap at 10 years
    
    # Acceleration factor for expertise
    acceleration = math.log(years + 1) / math.log(11)
    
    # Combine factors
    experience_factor = (base / 10.0) * acceleration
    return experience_factor
```

### Project Complexity Factor
```python
def calculate_complexity_score(project_metadata):
    factors = {
        "team_size": min(project_metadata.get("team_size", 1) / 50, 1.0),
        "project_duration": min(project_metadata.get("duration_months", 1) / 36, 1.0),
        "technical_complexity": project_metadata.get("complexity_score", 5) / 10.0,
        "lines_of_code": min(math.log(project_metadata.get("loc", 1000)) / 10, 1.0)
    }
    
    weighted_score = sum(factors.values()) / len(factors)
    return weighted_score
```

## Vector Database Integration

### Pinecone Example
```python
import pinecone

# Initialize
pinecone.init(api_key="your-key", environment="us-west1-gcp")
index = pinecone.Index("portfolio-embeddings")

# Upsert embeddings
vectors_to_upsert = [
    (f"skill_{skill}", embedding, {"type": "skill", "name": skill})
    for skill, embedding in skill_vectors.items()
]

index.upsert(vectors=vectors_to_upsert)
```

### Milvus Example
```python
from milvus import Collection, DataType

# Create collection
collection = Collection("portfolio_embeddings")

# Insert data
collection.insert(
    [
        [skill for skill in skills],  # skill names
        [vec.tolist() for vec in embeddings],  # embeddings
        ["skill"] * len(skills)  # types
    ]
)

collection.create_index(field_name="embedding", index_params={
    "metric_type": "L2",
    "index_type": "IVF_FLAT",
    "params": {"nlist": 128}
})
```

## Similarity Metrics

### Cosine Similarity (Recommended)
```python
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def calculate_cosine_similarity(vec1, vec2):
    return cosine_similarity([vec1], [vec2])[0][0]

# Batch similarity
similarities = cosine_similarity(embeddings1, embeddings2)
```

### Euclidean Distance
```python
from scipy.spatial.distance import euclidean

def calculate_euclidean_distance(vec1, vec2):
    distance = euclidean(vec1, vec2)
    # Convert to similarity (inverse)
    similarity = 1 / (1 + distance)
    return similarity
```

### Dot Product
```python
def calculate_dot_product_similarity(vec1, vec2):
    # Assumes normalized vectors
    return np.dot(vec1, vec2)
```

## Fine-Tuning Embeddings

### Domain-Specific Fine-Tuning
```python
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

model = SentenceTransformer('all-MiniLM-L6-v2')

# Training data: (sentence1, sentence2, label)
training_examples = [
    InputExample(texts=["Python", "Python programming"], label=0.9),
    InputExample(texts=["Python", "JavaScript"], label=0.3),
    InputExample(texts=["Deep Learning", "Neural Networks"], label=0.95)
]

train_dataloader = DataLoader(training_examples, shuffle=True, batch_size=16)
train_loss = losses.CosineSimilarityLoss(model)

model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=1,
    warmup_steps=100
)
```

## Caching and Optimization

### Embedding Cache Implementation
```python
import hashlib
import json
from datetime import datetime, timedelta

class EmbeddingCache:
    def __init__(self, ttl_days=30):
        self.cache = {}  # or use Redis
        self.ttl = timedelta(days=ttl_days)
    
    def get_cache_key(self, text):
        return hashlib.sha256(text.encode()).hexdigest()
    
    def get(self, text):
        key = self.get_cache_key(text)
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() - entry['timestamp'] < self.ttl:
                return entry['embedding']
        return None
    
    def set(self, text, embedding):
        key = self.get_cache_key(text)
        self.cache[key] = {
            'embedding': embedding,
            'timestamp': datetime.now()
        }
```

## Batch Processing

```python
def batch_embed_skills(skills, embedder, batch_size=32):
    embeddings = []
    for i in range(0, len(skills), batch_size):
        batch = skills[i:i+batch_size]
        batch_embeddings = embedder.encode(batch, convert_to_numpy=True)
        embeddings.extend(batch_embeddings)
    return embeddings
```

## Performance Metrics

### Embedding Quality
- **Intra-cluster similarity**: Average similarity within skill categories
- **Inter-cluster distance**: Minimum distance between different skill categories
- **Recall@k**: How often the correct skill appears in top-k results

### System Performance
- **Embedding latency**: Time to generate single embedding
- **Batch throughput**: Embeddings per second
- **Storage efficiency**: Bytes per embedding
- **Search latency**: Time to find similar embeddings
