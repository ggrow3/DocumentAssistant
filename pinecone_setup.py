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
    parser.add_argument('--index', default='personal-injury-assistant', help='Name for your Pinecone index')
    parser.add_argument('--cloud', default='aws', help='Cloud provider (aws, gcp, azure)')
    parser.add_argument('--region', default='us-west-2', help='Region (e.g., us-west-2, us-east-1)')
    
    args = parser.parse_args()
    
    # Check if pinecone-client is installed
    try:
        from pinecone import Pinecone
        try:
            from pinecone import ServerlessSpec
            has_serverless = True
        except ImportError:
            has_serverless = False
    except ImportError:
        print("Error: pinecone-client not installed")
        print("Please install it using: pip install pinecone-client")
        return
    
    # Get API key
    api_key = args.api_key or os.environ.get('PINECONE_API_KEY')
    if not api_key:
        api_key = input("Enter your Pinecone API key: ")
    
    # Initialize Pinecone client
    try:
        print("Initializing Pinecone client...")
        pc = Pinecone(api_key=api_key)
    except Exception as e:
        print(f"Error initializing Pinecone client: {str(e)}")
        return
    
    # List existing indexes
    try:
        indexes = pc.list_indexes().names()
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
                pc.delete_index(args.index)
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
        
        if has_serverless:
            # Create with ServerlessSpec
            pc.create_index(
                name=args.index,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=args.cloud,
                    region=args.region
                )
            )
        else:
            # Create with basic parameters
            pc.create_index(
                name=args.index,
                dimension=1536,
                metric="cosine"
            )
            
        print(f"Index '{args.index}' created successfully!")
        print("\nYou can now use this index in the Personal Injury Law Firm AI Assistant.")
        print(f"In the settings panel, select 'Pinecone' as the vector store type,")
        print(f"and enter '{args.index}' as the index name.")
    except Exception as e:
        print(f"Error creating index: {str(e)}")
        return

if __name__ == "__main__":
    main()