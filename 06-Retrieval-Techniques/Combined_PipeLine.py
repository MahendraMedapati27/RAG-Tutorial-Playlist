"""
Complete Advanced Retrieval Pipeline
Simple implementation without classes for easy understanding
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from sklearn.metrics.pairwise import cosine_similarity

# Install required packages:
# pip install sentence-transformers rank-bm25 scikit-learn numpy

# =============================================================================
# SAMPLE DATA
# =============================================================================

# Sample documents - you can replace with your own
documents = [
    "Machine learning algorithms are powerful tools for data analysis and prediction",
    "Deep learning neural networks can process complex patterns in data",
    "Python is a popular programming language for artificial intelligence",
    "Data science involves extracting insights from large datasets",
    "Natural language processing helps computers understand human language",
    "Computer vision enables machines to interpret and analyze visual information",
    "Supervised learning uses labeled data to train predictive models",
    "Unsupervised learning finds hidden patterns in unlabeled data",
    "Reinforcement learning trains agents through reward and punishment",
    "Big data analytics requires specialized tools and techniques",
    "Statistical analysis helps identify trends and patterns in data",
    "Database management systems store and organize large amounts of information",
    "Cloud computing provides scalable infrastructure for data processing",
    "API development enables communication between different software systems",
    "Web scraping extracts data from websites automatically"
]

# =============================================================================
# INITIALIZATION
# =============================================================================

print("Initializing retrieval pipeline...")

# Load the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create embeddings for all documents
doc_embeddings = model.encode(documents)

# Prepare documents for BM25 (sparse retrieval)
tokenized_docs = [doc.lower().split() for doc in documents]
bm25 = BM25Okapi(tokenized_docs)

print(f"Loaded {len(documents)} documents")
print(f"Created embeddings with shape: {doc_embeddings.shape}")
print("-" * 50)

# =============================================================================
# RETRIEVAL FUNCTIONS
# =============================================================================

def dense_retrieval(query, top_k=10):
    """Dense retrieval using embeddings"""
    query_embedding = model.encode([query])
    similarities = cosine_similarity(query_embedding, doc_embeddings)[0]
    
    # Get top results
    top_indices = np.argsort(similarities)[::-1][:top_k]
    results = [(documents[idx], similarities[idx]) for idx in top_indices]
    
    return results

def sparse_retrieval(query, top_k=10):
    """Sparse retrieval using BM25"""
    query_tokens = query.lower().split()
    scores = bm25.get_scores(query_tokens)
    
    # Get top results
    top_indices = np.argsort(scores)[::-1][:top_k]
    results = [(documents[idx], scores[idx]) for idx in top_indices]
    
    return results

def hybrid_retrieval(query, alpha=0.7, top_k=10):
    """
    Hybrid retrieval combining dense and sparse
    alpha: weight for dense retrieval (0.7 = 70% dense, 30% sparse)
    """
    # Get dense scores
    query_embedding = model.encode([query])
    dense_scores = cosine_similarity(query_embedding, doc_embeddings)[0]
    
    # Get sparse scores
    query_tokens = query.lower().split()
    sparse_scores = bm25.get_scores(query_tokens)
    
    # Normalize scores to 0-1 range
    dense_min, dense_max = dense_scores.min(), dense_scores.max()
    if dense_max > dense_min:
        dense_norm = (dense_scores - dense_min) / (dense_max - dense_min)
    else:
        dense_norm = dense_scores
    
    sparse_min, sparse_max = sparse_scores.min(), sparse_scores.max()
    if sparse_max > sparse_min:
        sparse_norm = (sparse_scores - sparse_min) / (sparse_max - sparse_min)
    else:
        sparse_norm = sparse_scores
    
    # Combine scores
    hybrid_scores = alpha * dense_norm + (1 - alpha) * sparse_norm
    
    # Get top results
    top_indices = np.argsort(hybrid_scores)[::-1][:top_k]
    results = [(documents[idx], hybrid_scores[idx]) for idx in top_indices]
    
    return results

def mmr_retrieval(query, lambda_param=0.7, top_k=5):
    """
    Maximum Marginal Relevance retrieval for diverse results
    lambda_param: balance between relevance and diversity
    """
    # Get query embedding
    query_embedding = model.encode([query])
    
    # Calculate relevance scores
    relevance_scores = cosine_similarity(query_embedding, doc_embeddings)[0]
    
    selected_docs = []
    selected_indices = []
    remaining_indices = list(range(len(documents)))
    
    # Select first document (highest relevance)
    first_idx = np.argmax(relevance_scores)
    selected_docs.append(documents[first_idx])
    selected_indices.append(first_idx)
    remaining_indices.remove(first_idx)
    
    # Select remaining documents using MMR
    for _ in range(min(top_k - 1, len(remaining_indices))):
        best_mmr_score = -float('inf')
        best_idx = None
        
        for idx in remaining_indices:
            # Relevance component
            relevance = relevance_scores[idx]
            
            # Diversity component (max similarity to selected docs)
            max_sim_to_selected = 0
            for selected_idx in selected_indices:
                sim = cosine_similarity(
                    doc_embeddings[idx].reshape(1, -1),
                    doc_embeddings[selected_idx].reshape(1, -1)
                )[0][0]
                max_sim_to_selected = max(max_sim_to_selected, sim)
            
            # MMR score
            mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim_to_selected
            
            if mmr_score > best_mmr_score:
                best_mmr_score = mmr_score
                best_idx = idx
        
        if best_idx is not None:
            selected_docs.append(documents[best_idx])
            selected_indices.append(best_idx)
            remaining_indices.remove(best_idx)
    
    return selected_docs

def advanced_retrieval_pipeline(query, config=None):
    """
    Complete advanced retrieval pipeline
    
    Args:
        query: search query
        config: configuration dictionary with parameters
    """
    # Default configuration
    if config is None:
        config = {
            'hybrid_alpha': 0.7,
            'mmr_lambda': 0.7,
            'initial_candidates': 10,
            'final_results': 5,
            'use_mmr': True
        }
    
    print(f"Query: '{query}'")
    print(f"Configuration: {config}")
    print("-" * 40)
    
    # Step 1: Hybrid retrieval to get initial candidates
    print("Step 1: Hybrid retrieval...")
    hybrid_results = hybrid_retrieval(
        query, 
        alpha=config['hybrid_alpha'], 
        top_k=config['initial_candidates']
    )
    
    # Step 2: Apply MMR for diversity (optional)
    if config['use_mmr']:
        print("Step 2: Applying MMR for diversity...")
        final_results = mmr_retrieval(
            query,
            lambda_param=config['mmr_lambda'],
            top_k=config['final_results']
        )
    else:
        print("Step 2: Skipping MMR, using hybrid results...")
        final_results = [doc for doc, score in hybrid_results[:config['final_results']]]
    
    return final_results

# =============================================================================
# EXAMPLE USAGE AND TESTING
# =============================================================================

def test_single_method(method_name, method_func, query, **kwargs):
    """Test a single retrieval method"""
    print(f"\n{method_name.upper()}")
    print("=" * 40)
    print(f"Query: '{query}'")
    
    results = method_func(query, **kwargs)
    
    if isinstance(results[0], tuple):  # Results with scores
        for i, (doc, score) in enumerate(results[:5], 1):
            print(f"{i}. Score: {score:.3f}")
            print(f"   {doc}")
    else:  # Results without scores (MMR)
        for i, doc in enumerate(results[:5], 1):
            print(f"{i}. {doc}")

def compare_all_methods(query):
    """Compare all retrieval methods"""
    print("\n" + "=" * 80)
    print(f"COMPARING ALL METHODS FOR: '{query}'")
    print("=" * 80)
    
    # Test each method
    test_single_method("Dense Retrieval", dense_retrieval, query, top_k=5)
    test_single_method("Sparse Retrieval", sparse_retrieval, query, top_k=5)
    test_single_method("Hybrid Retrieval", hybrid_retrieval, query, alpha=0.7, top_k=5)
    test_single_method("MMR Retrieval", mmr_retrieval, query, lambda_param=0.7, top_k=5)

def test_advanced_pipeline():
    """Test the complete advanced retrieval pipeline"""
    print("\n" + "=" * 80)
    print("TESTING ADVANCED RETRIEVAL PIPELINE")
    print("=" * 80)
    
    test_queries = [
        "machine learning algorithms",
        "python programming language",
        "data analysis techniques",
        "artificial intelligence applications"
    ]
    
    # Test different configurations
    configurations = {
        'Balanced': {
            'hybrid_alpha': 0.7,
            'mmr_lambda': 0.7,
            'initial_candidates': 10,
            'final_results': 5,
            'use_mmr': True
        },
        'Semantic Focus': {
            'hybrid_alpha': 0.9,
            'mmr_lambda': 0.6,
            'initial_candidates': 10,
            'final_results': 5,
            'use_mmr': True
        },
        'Keyword Focus': {
            'hybrid_alpha': 0.3,
            'mmr_lambda': 0.8,
            'initial_candidates': 10,
            'final_results': 5,
            'use_mmr': True
        },
        'High Diversity': {
            'hybrid_alpha': 0.7,
            'mmr_lambda': 0.5,
            'initial_candidates': 10,
            'final_results': 5,
            'use_mmr': True
        }
    }
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Testing query: '{query}'")
        print('='*60)
        
        for config_name, config in configurations.items():
            print(f"\n--- {config_name} Configuration ---")
            results = advanced_retrieval_pipeline(query, config)
            
            print("Results:")
            for i, doc in enumerate(results, 1):
                print(f"{i}. {doc}")

# =============================================================================
# INTERACTIVE SEARCH FUNCTION
# =============================================================================

def interactive_search():
    """Interactive search interface"""
    print("\n" + "=" * 60)
    print("INTERACTIVE SEARCH")
    print("=" * 60)
    print("Type your queries (or 'quit' to exit)")
    
    while True:
        query = input("\nEnter your search query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not query:
            print("Please enter a valid query.")
            continue
        
        # Use the advanced pipeline with default config
        results = advanced_retrieval_pipeline(query)
        
        print("\nResults:")
        for i, doc in enumerate(results, 1):
            print(f"{i}. {doc}")

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("Advanced Retrieval Pipeline Demo")
    print("=" * 50)
    
    # Test individual methods
    test_query = "machine learning algorithms"
    compare_all_methods(test_query)
    
    # Test advanced pipeline
    test_advanced_pipeline()
    
    # Option for interactive search
    print("\n" + "=" * 60)
    response = input("Would you like to try interactive search? (y/n): ").strip().lower()
    if response in ['y', 'yes']:
        interactive_search()
    
    print("\nDemo completed!")
    
    # Usage examples for different domains
    print("\n" + "=" * 60)
    print("CONFIGURATION EXAMPLES FOR DIFFERENT DOMAINS")
    print("=" * 60)
    
    domain_configs = {
        'E-commerce': {
            'hybrid_alpha': 0.6,
            'mmr_lambda': 0.6,
            'use_mmr': True,
            'description': 'Balance exact matches with semantic similarity, good diversity for alternatives'
        },
        'Legal Documents': {
            'hybrid_alpha': 0.3,
            'mmr_lambda': 0.8,
            'use_mmr': True,
            'description': 'Heavy emphasis on exact terms, high relevance priority'
        },
        'Research & Discovery': {
            'hybrid_alpha': 0.8,
            'mmr_lambda': 0.5,
            'use_mmr': True,
            'description': 'Semantic understanding important, high diversity for exploration'
        },
        'Customer Support': {
            'hybrid_alpha': 0.7,
            'mmr_lambda': 0.7,
            'use_mmr': True,
            'description': 'Balanced approach for comprehensive help'
        }
    }
    
    for domain, config in domain_configs.items():
        print(f"\n{domain}:")
        for key, value in config.items():
            print(f"  {key}: {value}")