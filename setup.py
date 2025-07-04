#!/usr/bin/env python3
"""
Setup script for AWS Language Chat Buddy
"""

import os
import sys
import subprocess
import json

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_aws_cli():
    """Check if AWS CLI is installed and configured"""
    print("Checking AWS CLI...")
    try:
        result = subprocess.run(['aws', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ AWS CLI detected: {result.stdout.strip()}")
            
            # Check if configured
            result = subprocess.run(['aws', 'configure', 'list'], capture_output=True, text=True)
            if 'access_key' in result.stdout:
                print("✅ AWS CLI is configured")
                return True
            else:
                print("⚠️ AWS CLI is not configured. Run 'aws configure' first.")
                return False
        else:
            print("❌ AWS CLI not found. Please install AWS CLI.")
            return False
    except FileNotFoundError:
        print("❌ AWS CLI not found. Please install AWS CLI.")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def setup_config():
    """Set up configuration file"""
    print("Setting up configuration...")
    
    config_template = 'config.py.template'
    config_file = 'config.py'
    
    if os.path.exists(config_file):
        print("⚠️ config.py already exists. Skipping...")
        return True
    
    if os.path.exists(config_template):
        try:
            with open(config_template, 'r') as f:
                content = f.read()
            
            with open(config_file, 'w') as f:
                f.write(content)
            
            print("✅ Configuration file created. Please edit config.py with your settings.")
            return True
        except Exception as e:
            print(f"❌ Failed to create config file: {e}")
            return False
    else:
        print("⚠️ config.py.template not found")
        return False

def setup_zappa():
    """Set up Zappa configuration"""
    print("Setting up Zappa...")
    
    zappa_file = 'zappa_settings.json'
    
    if not os.path.exists(zappa_file):
        print("❌ zappa_settings.json not found")
        return False
    
    try:
        with open(zappa_file, 'r') as f:
            config = json.load(f)
        
        # Check if S3 bucket names are configured
        dev_bucket = config.get('dev', {}).get('s3_bucket', '')
        prod_bucket = config.get('production', {}).get('s3_bucket', '')
        
        if 'your-bucket-name' in dev_bucket or 'your-bucket-name' in prod_bucket:
            print("⚠️ Please update S3 bucket names in zappa_settings.json")
            return False
        
        print("✅ Zappa configuration looks good")
        return True
    except Exception as e:
        print(f"❌ Failed to validate Zappa config: {e}")
        return False

def run_tests():
    """Run basic tests"""
    print("Running basic tests...")
    
    try:
        # Test scenario loading
        test_file = 'zappa_backend/scenarios/friend.json'
        if os.path.exists(test_file):
            with open(test_file, 'r') as f:
                json.load(f)
            print("✅ Scenario files are valid JSON")
        else:
            print("❌ Scenario files not found")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Tests failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 AWS Language Chat Buddy Setup")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("AWS CLI", check_aws_cli),
        ("Dependencies", install_dependencies),
        ("Configuration", setup_config),
        ("Zappa Setup", setup_zappa),
        ("Basic Tests", run_tests)
    ]
    
    for check_name, check_func in checks:
        print(f"\n🔍 {check_name}")
        if not check_func():
            print(f"\n❌ Setup failed at: {check_name}")
            print("\nPlease fix the issues above and run setup again.")
            return 1
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit config.py with your AWS settings")
    print("2. Update S3 bucket names in zappa_settings.json")
    print("3. Enable AWS Bedrock model access in AWS Console")
    print("4. Run: python example_usage.py (for local testing)")
    print("5. Run: zappa deploy dev (for AWS deployment)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
