#!/usr/bin/env python3
"""
Langfuse Setup Script
Helps users set up Langfuse monitoring for the LangGraph application
"""
import os
import json
import requests
import time
import subprocess


def wait_for_langfuse(host="http://localhost:3000", timeout=120):
    """Wait for Langfuse to be ready"""
    print(f"Waiting for Langfuse at {host}...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{host}/api/public/health", timeout=5)
            if response.status_code == 200:
                print("✅ Langfuse is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print("⏳ Waiting for Langfuse to start...")
        time.sleep(5)
    
    print("❌ Timeout waiting for Langfuse")
    return False


def create_langfuse_project():
    """Instructions for creating a Langfuse project"""
    print("\n🚀 Setting up Langfuse monitoring...")
    print("\n📋 Follow these steps:")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Create an account or sign in")
    print("3. Create a new project")
    print("4. Go to Settings > API Keys")
    print("5. Copy the Secret Key and Public Key")
    print("6. Add them to your .env file:")
    print("   LANGFUSE_SECRET_KEY=sk-lf-...")
    print("   LANGFUSE_PUBLIC_KEY=pk-lf-...")
    print("   LANGFUSE_HOST=http://localhost:3000")


def main():
    print("🔧 Langfuse Setup for LangGraph Application")
    print("=" * 50)
    
    # Check if Docker Compose is available
    try:
        subprocess.run(["docker-compose", "--version"], 
                      capture_output=True, check=True)
        print("✅ Docker Compose is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker Compose not found. Please install Docker Compose first.")
        return
    
    # Start Langfuse services
    print("\n🐳 Starting Langfuse services...")
    try:
        subprocess.run([
            "docker-compose", "up", "-d", 
            "langfuse-db", "langfuse-server"
        ], check=True)
        print("✅ Langfuse services started")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start services: {e}")
        return
    
    # Wait for Langfuse to be ready
    if wait_for_langfuse():
        create_langfuse_project()
        
        print("\n🎯 Next steps:")
        print("1. Complete the Langfuse setup in your browser")
        print("2. Update your .env file with the API keys")
        print("3. Restart your application: docker-compose up --build")
        print("4. Your LLM calls will now be monitored in Langfuse!")
        
        print(f"\n📊 Langfuse Dashboard: http://localhost:3000")
    else:
        print("❌ Failed to start Langfuse. Check Docker logs:")
        print("docker-compose logs langfuse-server")


if __name__ == "__main__":
    main()