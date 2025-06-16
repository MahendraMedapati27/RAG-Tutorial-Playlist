import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sentence_transformers import SentenceTransformer
import warnings
warnings.filterwarnings('ignore')

# Database imports
import chromadb
try:
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    print("Pinecone not installed. Install with: pip install pinecone-client")

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("FAISS not installed. Install with: pip install faiss-cpu")

import os
from typing import List, Dict, Tuple, Optional
import json

class VectorDatabaseComparison:
    """
    Comprehensive comparison of ChromaDB, Pinecone, and FAISS vector databases.
    Tests setup complexity, search performance, accuracy, and feature richness.
    """
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.documents = [
            "The quick brown fox jumps over the lazy dog",
            "Artificial intelligence is transforming technology",
            "Python is a popular programming language",
            "Machine learning models require large datasets",
            "Vector databases enable fast similarity search",
            "Natural language processing analyzes text data",
            "Deep learning uses neural networks",
            "Data science combines statistics and programming",
            "Cloud computing provides scalable infrastructure",
            "Software development involves writing code",
            "Neural networks are inspired by biological neurons",
            "Big data analytics helps businesses make decisions",
            "Computer vision enables machines to understand images",
            "Reinforcement learning trains agents through rewards",
            "Natural language understanding is a key AI challenge",
            "Distributed systems handle large-scale computing",
            "Database management systems store and retrieve data",
            "Web development creates interactive applications",
            "Mobile applications run on smartphones and tablets",
            "Cybersecurity protects digital assets from threats"
        ]
        self.embeddings = None
        self.test_queries = [
            "What is artificial intelligence?",
            "How do machine learning algorithms work?",
            "What are neural networks?",
            "How does data science help businesses?",
            "What is computer programming?"
        ]
        self.results = {}
        
    def generate_embeddings(self):
        """Generate embeddings for all documents."""
        print("Generating embeddings for documents...")
        start_time = time.time()
        self.embeddings = self.model.encode(self.documents)
        embedding_time = time.time() - start_time
        print(f"Generated {len(self.embeddings)} embeddings in {embedding_time:.3f} seconds")
        print(f"Embedding dimension: {self.embeddings.shape[1]}")
        return embedding_time

    def setup_chromadb(self) -> Tuple[bool, float, str]:
        """Setup ChromaDB and measure setup time."""
        print("\n=== Setting up ChromaDB ===")
        try:
            start_time = time.time()
            
            # Initialize ChromaDB
            self.chroma_client = chromadb.Client()
            
            # Create collection
            collection_name = "comparison_test"
            try:
                self.chroma_collection = self.chroma_client.get_collection(collection_name)
                self.chroma_client.delete_collection(collection_name)
            except:
                pass
            
            self.chroma_collection = self.chroma_client.create_collection(
                name=collection_name,
                metadata={"description": "Database comparison test"}
            )
            
            # Add documents
            ids = [f"doc_{i}" for i in range(len(self.documents))]
            metadatas = [{"source": "comparison", "index": i} for i in range(len(self.documents))]
            
            self.chroma_collection.add(
                documents=self.documents,
                embeddings=self.embeddings.tolist(),
                ids=ids,
                metadatas=metadatas
            )
            
            setup_time = time.time() - start_time
            print(f"✅ ChromaDB setup completed in {setup_time:.3f} seconds")
            print(f"   Documents stored: {self.chroma_collection.count()}")
            
            return True, setup_time, "Success"
            
        except Exception as e:
            print(f"❌ ChromaDB setup failed: {str(e)}")
            return False, 0, str(e)

    def setup_pinecone(self) -> Tuple[bool, float, str]:
        """Setup Pinecone and measure setup time."""
        print("\n=== Setting up Pinecone ===")
        
        if not PINECONE_AVAILABLE:
            return False, 0, "Pinecone not installed"
            
        try:
            start_time = time.time()
            
            # Initialize Pinecone with direct API key
            pc = Pinecone(api_key='pcsk_2GZce8_2VH6C9y7ToCoDeuWizMeJSh2PEmGyNQ46ugBGFn8ny7h4DtW5T3oRkGvL2yZ5kf')
            
            # Create index
            index_name = "comparison-test"
            dimension = self.embeddings.shape[1]
            
            # Delete existing index if it exists
            if index_name in pc.list_indexes().names():
                pc.delete_index(index_name)
                time.sleep(5)  # Wait for deletion
            
            # Create new index with ServerlessSpec
            pc.create_index(
                name=index_name,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
            
            # Wait for index to be ready
            time.sleep(10)
            
            # Connect to index
            self.pinecone_index = pc.Index(index_name)
            
            # Prepare and upload vectors
            vectors_to_upsert = []
            for i, (doc, embedding) in enumerate(zip(self.documents, self.embeddings)):
                vectors_to_upsert.append({
                    'id': f'doc_{i}',
                    'values': embedding.tolist(),
                    'metadata': {
                        'text': doc,
                        'source': 'comparison',
                        'index': i
                    }
                })
            
            # Upload vectors
            upsert_response = self.pinecone_index.upsert(vectors=vectors_to_upsert)
            
            # Wait for indexing
            time.sleep(5)
            
            setup_time = time.time() - start_time
            print(f"✅ Pinecone setup completed in {setup_time:.3f} seconds")
            print(f"   Vectors upserted: {upsert_response['upserted_count']}")
            
            return True, setup_time, "Success"
            
        except Exception as e:
            print(f"❌ Pinecone setup failed: {str(e)}")
            return False, 0, str(e)

    def setup_faiss(self) -> Tuple[bool, float, str]:
        """Setup FAISS and measure setup time."""
        print("\n=== Setting up FAISS ===")
        
        if not FAISS_AVAILABLE:
            return False, 0, "FAISS not installed"
            
        try:
            start_time = time.time()
            
            # Convert embeddings to numpy array
            embeddings_np = np.array(self.embeddings).astype('float32')
            
            # Create FAISS index
            dimension = embeddings_np.shape[1]
            self.faiss_index = faiss.IndexFlatIP(dimension)  # Inner Product for cosine similarity
            
            # Normalize vectors for cosine similarity
            faiss.normalize_L2(embeddings_np)
            
            # Add vectors to index
            self.faiss_index.add(embeddings_np)
            
            # Store documents separately (FAISS doesn't store metadata)
            self.faiss_documents = self.documents.copy()
            
            setup_time = time.time() - start_time
            print(f"✅ FAISS setup completed in {setup_time:.3f} seconds")
            print(f"   Vectors indexed: {self.faiss_index.ntotal}")
            
            return True, setup_time, "Success"
            
        except Exception as e:
            print(f"❌ FAISS setup failed: {str(e)}")
            return False, 0, str(e)

    def benchmark_search_performance(self, num_iterations: int = 100) -> Dict:
        """Benchmark search performance across all databases."""
        print(f"\n=== Benchmarking Search Performance ({num_iterations} iterations) ===")
        
        performance_results = {
            'chromadb': {'times': [], 'success': False},
            'pinecone': {'times': [], 'success': False},
            'faiss': {'times': [], 'success': False}
        }
        
        # Test query
        query = "What is artificial intelligence and machine learning?"
        query_embedding = self.model.encode([query])
        
        # Benchmark ChromaDB
        if hasattr(self, 'chroma_collection'):
            print("Benchmarking ChromaDB...")
            try:
                for _ in range(num_iterations):
                    start_time = time.time()
                    results = self.chroma_collection.query(
                        query_embeddings=query_embedding.tolist(),
                        n_results=3
                    )
                    search_time = time.time() - start_time
                    performance_results['chromadb']['times'].append(search_time)
                performance_results['chromadb']['success'] = True
                avg_time = np.mean(performance_results['chromadb']['times'])
                print(f"   ChromaDB average search time: {avg_time*1000:.2f}ms")
            except Exception as e:
                print(f"   ChromaDB benchmark failed: {e}")
        
        # Benchmark Pinecone
        if hasattr(self, 'pinecone_index'):
            print("Benchmarking Pinecone...")
            try:
                for _ in range(num_iterations):
                    start_time = time.time()
                    results = self.pinecone_index.query(
                        vector=query_embedding.tolist(),
                        top_k=3,
                        include_metadata=True
                    )
                    search_time = time.time() - start_time
                    performance_results['pinecone']['times'].append(search_time)
                performance_results['pinecone']['success'] = True
                avg_time = np.mean(performance_results['pinecone']['times'])
                print(f"   Pinecone average search time: {avg_time*1000:.2f}ms")
            except Exception as e:
                print(f"   Pinecone benchmark failed: {e}")
        
        # Benchmark FAISS
        if hasattr(self, 'faiss_index'):
            print("Benchmarking FAISS...")
            try:
                query_np = np.array(query_embedding).astype('float32')
                faiss.normalize_L2(query_np)
                
                for _ in range(num_iterations):
                    start_time = time.time()
                    scores, indices = self.faiss_index.search(query_np, 3)
                    search_time = time.time() - start_time
                    performance_results['faiss']['times'].append(search_time)
                performance_results['faiss']['success'] = True
                avg_time = np.mean(performance_results['faiss']['times'])
                print(f"   FAISS average search time: {avg_time*1000:.2f}ms")
            except Exception as e:
                print(f"   FAISS benchmark failed: {e}")
        
        return performance_results

    def test_search_accuracy(self) -> Dict:
        """Test search accuracy and consistency across databases."""
        print("\n=== Testing Search Accuracy ===")
        
        accuracy_results = {}
        
        for query in self.test_queries:
            print(f"\nQuery: '{query}'")
            query_embedding = self.model.encode([query])
            query_results = {}
            
            # ChromaDB search
            if hasattr(self, 'chroma_collection'):
                try:
                    results = self.chroma_collection.query(
                        query_embeddings=query_embedding.tolist(),
                        n_results=3,
                        include=['documents', 'distances']
                    )
                    query_results['chromadb'] = {
                        'documents': results['documents'][0],
                        'scores': [1 - d for d in results['distances'][0]]  # Convert distance to similarity
                    }
                    print("  ChromaDB results:")
                    for i, (doc, score) in enumerate(zip(results['documents'][0], query_results['chromadb']['scores'])):
                        print(f"    {i+1}. {score:.3f}: {doc[:50]}...")
                except Exception as e:
                    print(f"  ChromaDB search failed: {e}")
            
            # Pinecone search
            if hasattr(self, 'pinecone_index'):
                try:
                    results = self.pinecone_index.query(
                        vector=query_embedding.tolist(),
                        top_k=3,
                        include_metadata=True
                    )
                    query_results['pinecone'] = {
                        'documents': [match['metadata']['text'] for match in results['matches']],
                        'scores': [match['score'] for match in results['matches']]
                    }
                    print("  Pinecone results:")
                    for i, match in enumerate(results['matches']):
                        print(f"    {i+1}. {match['score']:.3f}: {match['metadata']['text'][:50]}...")
                except Exception as e:
                    print(f"  Pinecone search failed: {e}")
            
            # FAISS search
            if hasattr(self, 'faiss_index'):
                try:
                    query_np = np.array(query_embedding).astype('float32')
                    faiss.normalize_L2(query_np)
                    scores, indices = self.faiss_index.search(query_np, 3)
                    
                    query_results['faiss'] = {
                        'documents': [self.faiss_documents[idx] for idx in indices[0]],
                        'scores': scores[0].tolist()
                    }
                    print("  FAISS results:")
                    for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                        print(f"    {i+1}. {score:.3f}: {self.faiss_documents[idx][:50]}...")
                except Exception as e:
                    print(f"  FAISS search failed: {e}")
            
            accuracy_results[query] = query_results
        
        return accuracy_results

    def analyze_feature_richness(self) -> Dict:
        """Analyze feature richness of each database."""
        print("\n=== Analyzing Feature Richness ===")
        
        features = {
            'chromadb': {
                'metadata_support': True,
                'built_in_embeddings': False,
                'cloud_managed': False,
                'auto_scaling': False,
                'real_time_updates': True,
                'backup_restore': True,
                'monitoring': False,
                'multi_tenancy': True,
                'cost': 'Free',
                'setup_complexity': 'Low',
                'production_ready': 'Medium'
            },
            'pinecone': {
                'metadata_support': True,
                'built_in_embeddings': False,
                'cloud_managed': True,
                'auto_scaling': True,
                'real_time_updates': True,
                'backup_restore': True,
                'monitoring': True,
                'multi_tenancy': True,
                'cost': 'Paid (~$70/month for 1M vectors)',
                'setup_complexity': 'Medium',
                'production_ready': 'High'
            },
            'faiss': {
                'metadata_support': False,
                'built_in_embeddings': False,
                'cloud_managed': False,
                'auto_scaling': False,
                'real_time_updates': True,
                'backup_restore': True,
                'monitoring': False,
                'multi_tenancy': False,
                'cost': 'Free',
                'setup_complexity': 'High',
                'production_ready': 'High (with effort)'
            }
        }
        
        for db_name, db_features in features.items():
            print(f"\n{db_name.upper()} Features:")
            for feature, value in db_features.items():
                status = "✅" if value is True else "❌" if value is False else "ℹ️"
                print(f"  {status} {feature.replace('_', ' ').title()}: {value}")
        
        return features

    def generate_comparison_report(self, performance_results: Dict, accuracy_results: Dict, features: Dict):
        """Generate a comprehensive comparison report."""
        print("\n" + "="*60)
        print("COMPREHENSIVE DATABASE COMPARISON REPORT")
        print("="*60)
        
        # Performance Summary
        print("\n📊 PERFORMANCE SUMMARY")
        print("-" * 30)
        
        for db_name, results in performance_results.items():
            if results['success'] and results['times']:
                avg_time = np.mean(results['times']) * 1000  # Convert to ms
                min_time = np.min(results['times']) * 1000
                max_time = np.max(results['times']) * 1000
                std_time = np.std(results['times']) * 1000
                
                print(f"\n{db_name.upper()}:")
                print(f"  Average: {avg_time:.2f}ms")
                print(f"  Min: {min_time:.2f}ms")
                print(f"  Max: {max_time:.2f}ms")
                print(f"  Std Dev: {std_time:.2f}ms")
            else:
                print(f"\n{db_name.upper()}: Not available or failed")
        
        # Recommendations
        print("\n🎯 RECOMMENDATIONS")
        print("-" * 20)
        print("\n🚀 For Learning/Prototyping:")
        print("   → ChromaDB (Easiest setup, focus on concepts)")
        
        print("\n🏢 For Production (Small-Medium Scale):")
        print("   → Pinecone (Managed, reliable) or ChromaDB (Self-hosted)")
        
        print("\n⚡ For High Performance/Large Scale:")
        print("   → FAISS (Maximum speed) or Pinecone (Managed performance)")
        
        print("\n💰 For Budget-Conscious:")
        print("   → ChromaDB or FAISS (Both free)")
        
        print("\n🔧 For Complex Requirements:")
        print("   → Weaviate (Multi-modal, advanced features)")

    def create_visualization(self, performance_results: Dict):
        """Create performance visualization."""
        print("\n📈 Creating performance visualization...")
        
        # Prepare data for plotting
        db_names = []
        avg_times = []
        
        for db_name, results in performance_results.items():
            if results['success'] and results['times']:
                db_names.append(db_name.upper())
                avg_times.append(np.mean(results['times']) * 1000)  # Convert to ms
        
        if not db_names:
            print("No performance data available for visualization")
            return
        
        # Create the plot
        plt.figure(figsize=(10, 6))
        
        # Bar plot
        bars = plt.bar(db_names, avg_times, color=['#3498db', '#e74c3c', '#2ecc71'])
        
        # Customize the plot
        plt.title('Vector Database Performance Comparison', fontsize=16, fontweight='bold')
        plt.xlabel('Database', fontsize=12)
        plt.ylabel('Average Search Time (ms)', fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar, time in zip(bars, avg_times):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{time:.2f}ms', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('vector_database_performance_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("Performance comparison chart saved as 'vector_database_performance_comparison.png'")

    def save_results_to_json(self, performance_results: Dict, accuracy_results: Dict, features: Dict):
        """Save all results to JSON file."""
        print("\n💾 Saving results to JSON...")
        
        # Prepare results for JSON serialization
        json_results = {
            'performance': {},
            'accuracy': accuracy_results,
            'features': features,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_documents': len(self.documents),
                'embedding_dimension': self.embeddings.shape[1] if self.embeddings is not None else 0,
                'test_queries': len(self.test_queries)
            }
        }
        
        # Process performance results
        for db_name, results in performance_results.items():
            if results['success'] and results['times']:
                json_results['performance'][db_name] = {
                    'average_time_ms': float(np.mean(results['times']) * 1000),
                    'min_time_ms': float(np.min(results['times']) * 1000),
                    'max_time_ms': float(np.max(results['times']) * 1000),
                    'std_dev_ms': float(np.std(results['times']) * 1000),
                    'total_queries': len(results['times'])
                }
            else:
                json_results['performance'][db_name] = {'status': 'failed or not available'}
        
        # Save to file
        with open('vector_database_comparison_results.json', 'w') as f:
            json.dump(json_results, f, indent=2)
        
        print("Results saved to 'vector_database_comparison_results.json'")

    def run_full_comparison(self):
        """Run the complete database comparison."""
        print("🚀 Starting Comprehensive Vector Database Comparison")
        print("="*60)
        
        # Generate embeddings
        embedding_time = self.generate_embeddings()
        
        # Setup databases
        setup_results = {}
        setup_results['chromadb'] = self.setup_chromadb()
        setup_results['pinecone'] = self.setup_pinecone()
        setup_results['faiss'] = self.setup_faiss()
        
        # Print setup summary
        print("\n📋 SETUP SUMMARY")
        print("-" * 20)
        for db_name, (success, time_taken, message) in setup_results.items():
            status = "✅" if success else "❌"
            print(f"{status} {db_name.upper()}: {time_taken:.3f}s - {message}")
        
        # Performance benchmarking
        performance_results = self.benchmark_search_performance()
        
        # Accuracy testing
        accuracy_results = self.test_search_accuracy()
        
        # Feature analysis
        features = self.analyze_feature_richness()
        
        # Generate comprehensive report
        self.generate_comparison_report(performance_results, accuracy_results, features)
        
        # Create visualization
        self.create_visualization(performance_results)
        
        # Save results
        self.save_results_to_json(performance_results, accuracy_results, features)
        
        print(f"\n🎉 Comparison completed! Check the generated files for detailed results.")


def main():
    """Main function to run the comparison."""
    # Run comparison
    comparator = VectorDatabaseComparison()
    comparator.run_full_comparison()


if __name__ == "__main__":
    main()