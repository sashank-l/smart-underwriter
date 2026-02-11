import os
import sys

# Ensure we can import app modules if needed, or just use fastembed directly
try:
    from fastembed import TextEmbedding
except ImportError:
    print("FastEmbed not installed. Skipping pre-download.")
    sys.exit(0)

def download_model():
    model_name = "BAAI/bge-small-en-v1.5" # Hardcoded or matching config
    print(f"Pre-downloading FastEmbed model: {model_name}...")
    
    # This triggers the download and caching
    model = TextEmbedding(model_name=model_name)
    
    print(f"Successfully downloaded {model_name}!")

if __name__ == "__main__":
    download_model()
