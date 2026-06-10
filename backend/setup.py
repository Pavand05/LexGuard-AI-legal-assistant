#!/usr/bin/env python3
"""
Setup script for the Legal AI Assistant
This script helps install dependencies and download a local LLM model.
"""

import os
import sys
import subprocess
import requests
from pathlib import Path

def install_requirements():
    """Install Python requirements"""
    print("Installing Python requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False
    return True

def download_model():
    """Download a local LLM model"""
    print("\n📥 Downloading local LLM model...")
    
    # Create models directory
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # You can choose from different models
    models = {
        "1": {
            "name": "llama-2-7b-chat.gguf",
            "url": "https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf",
            "size": "~4GB"
        },
        "2": {
            "name": "mistral-7b-instruct.gguf", 
            "url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
            "size": "~4GB"
        }
    }
    
    print("Available models:")
    for key, model in models.items():
        print(f"  {key}. {model['name']} ({model['size']})")
    
    choice = input("\nSelect a model to download (1-2) or press Enter to skip: ").strip()
    
    if not choice or choice not in models:
        print("Skipping model download. You can download manually later.")
        return True
    
    selected_model = models[choice]
    model_path = models_dir / selected_model["name"]
    
    if model_path.exists():
        print(f"✅ Model {selected_model['name']} already exists!")
        return True
    
    print(f"Downloading {selected_model['name']}...")
    print("This may take a while depending on your internet connection.")
    
    try:
        response = requests.get(selected_model["url"], stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(model_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rDownload progress: {percent:.1f}%", end="", flush=True)
        
        print(f"\n✅ Model downloaded successfully to {model_path}")
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to download model: {e}")
        print("You can download the model manually from HuggingFace.")
        return False

def create_config():
    """Create configuration file"""
    config_content = """# Legal AI Assistant Configuration

# Path to your local LLM model (optional)
# MODEL_PATH = "models/llama-2-7b-chat.gguf"

# Processing settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Risk assessment thresholds
HIGH_RISK_KEYWORDS = ["liability", "indemnification", "damages", "breach"]
MEDIUM_RISK_KEYWORDS = ["termination", "confidentiality", "non-compete"]
LOW_RISK_KEYWORDS = ["payment", "governing law", "jurisdiction"]
"""
    
    config_path = Path("config.py")
    if not config_path.exists():
        with open(config_path, 'w') as f:
            f.write(config_content)
        print("✅ Configuration file created: config.py")
    else:
        print("ℹ️  Configuration file already exists: config.py")

def main():
    """Main setup function"""
    print("🚀 Legal AI Assistant Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Download model
    download_model()
    
    # Create config
    create_config()
    
    print("\n🎉 Setup completed!")
    print("\nNext steps:")
    print("1. If you downloaded a model, update the MODEL_PATH in config.py")
    print("2. Run: python app.py")
    print("3. Open http://localhost:5000 in your browser")
    print("\nFor manual model download, visit:")
    print("https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF")
    print("https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF")

if __name__ == "__main__":
    main() 