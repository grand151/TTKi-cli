#!/usr/bin/env python3
"""
Test script to verify the Ubuntu sandbox development environment setup.
"""

import sys
import subprocess
import importlib
import os

def test_python_version():
    """Test Python version."""
    print("=== Testing Python Version ===")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print("✓ Python is working correctly\n")

def test_packages():
    """Test installed Python packages."""
    print("=== Testing Python Packages ===")
    packages = [
        'numpy', 'pandas', 'matplotlib', 'seaborn', 'scikit-learn',
        'flask', 'fastapi', 'requests', 'jupyter'
    ]
    
    for package in packages:
        try:
            importlib.import_module(package)
            print(f"✓ {package} is installed and importable")
        except ImportError:
            print(f"✗ {package} is not available")
    print()

def test_system_tools():
    """Test system tools availability."""
    print("=== Testing System Tools ===")
    tools = [
        'git', 'gcc', 'g++', 'make', 'cmake', 'node', 'npm', 
        'docker', 'sqlite3', 'jq', 'curl', 'wget'
    ]
    
    for tool in tools:
        try:
            result = subprocess.run(['which', tool], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ {tool} is available at {result.stdout.strip()}")
            else:
                print(f"✗ {tool} is not available")
        except Exception as e:
            print(f"✗ Error checking {tool}: {e}")
    print()

def test_virtual_environment():
    """Test virtual environment."""
    print("=== Testing Virtual Environment ===")
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ Running in virtual environment")
        print(f"Virtual environment path: {sys.prefix}")
    else:
        print("✗ Not running in virtual environment")
    print()

def test_file_system():
    """Test file system permissions and structure."""
    print("=== Testing File System ===")
    test_dir = "/home/ubuntu/dev_environment"
    if os.path.exists(test_dir):
        print(f"✓ Development directory exists: {test_dir}")
    else:
        print(f"✗ Development directory missing: {test_dir}")
    
    # Test write permissions
    test_file = "/tmp/sandbox_test.txt"
    try:
        with open(test_file, 'w') as f:
            f.write("Test file")
        os.remove(test_file)
        print("✓ File system write permissions working")
    except Exception as e:
        print(f"✗ File system write error: {e}")
    print()

def test_network():
    """Test network connectivity."""
    print("=== Testing Network Connectivity ===")
    try:
        import requests
        response = requests.get("https://httpbin.org/get", timeout=10)
        if response.status_code == 200:
            print("✓ Network connectivity working")
        else:
            print(f"✗ Network test failed with status: {response.status_code}")
    except Exception as e:
        print(f"✗ Network connectivity error: {e}")
    print()

def main():
    """Run all tests."""
    print("🚀 Ubuntu Sandbox Development Environment Test Suite")
    print("=" * 60)
    
    test_python_version()
    test_packages()
    test_system_tools()
    test_virtual_environment()
    test_file_system()
    test_network()
    
    print("=" * 60)
    print("✅ Environment testing completed!")

if __name__ == "__main__":
    main()

