"""
Pinecone Setup Script for Personal Injury Law Firm AI Assistant

This script helps you set up a Pinecone index for use with the Personal Injury Law Firm
AI Assistant. It will create a new Pinecone index with the correct dimension (1536) for
use with OpenAI embeddings.

Usage:
    python pinecone_setup.py

Requirements:
    - Pinecone API key
    - pinecone-client library installed
"""

import os
import argparse

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Set up Pinecone index for Personal Injury Law Firm AI Assistant')
    parser.add_argument('--api-key', help='Your Pinecone API key')
    parser.add_argument('--environment', default='us-west1-gcp', help='Pinecone environment')
    parser.add_argument('--index', default='personal-injury-assistant', help='Name for your Pinecone index')
    
    args = parser.parse_args()
    
    # Check if pinecone-client is installed
    try:
        import pinecone
    except ImportError:
        print("Error: pinecone-client not installed")
        print("Please install it using: pip install pinecone-client")
        return
    
    # Get API key
    api_key = args.api_key or os.environ.get('PINECONE_API_KEY')
    if not api_key:
        api_key = input("Enter your Pinecone API key: ")
    
    # Initialize Pinecone
    try:
        print(f"Initializing Pinecone with environment: {args.environment}")
        pinecone.init(api_key=api_key, environment=args.environment)
    except Exception as e:
        print(f"Error initializing Pinecone: {str(e)}")
        return
    
    # List existing indexes
    try:
        indexes = pinecone.list_indexes()
        print(f"Current indexes: {', '.join(indexes) if indexes else 'None'}")
    except Exception as e:
        print(f"Error listing indexes: {str(e)}")
        return
    
    # Check if index already exists
    if args.index in indexes:
        print(f"Index '{args.index}' already exists")
        proceed = input("Do you want to delete and recreate it? (y/n): ")
        if proceed.lower() == 'y':
            try:
                print(f"Deleting index '{args.index}'...")
                pinecone.delete_index(args.index)
                print("Index deleted successfully")
            except Exception as e:
                print(f"Error deleting index: {str(e)}")
                return
        else:
            print("Keeping existing index")
            return
    
    # Create new index
    try:
        print(f"Creating index '{args.index}' with dimension=1536...")
        pinecone.create_index(
            name=args.index,
            dimension=1536,
            metric="cosine"
        )
        print(f"Index '{args.index}' created successfully!")
        print("\nYou can now use this index in the Personal Injury Law Firm AI Assistant.")
        print(f"In the settings panel, select 'Pinecone' as the vector store type,")
        print(f"enter '{args.environment}' as the environment, and '{args.index}' as the index name.")
    except Exception as e:
        print(f"Error creating index: {str(e)}")
        return

if __name__ == "__main__":
    main()