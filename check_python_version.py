#!/usr/bin/env python3
"""
Check if the current Python version is compatible with AWS App Runner.
AWS App Runner supports Python 3.11 for this application.
"""

import sys
import platform

def main():
    python_version = sys.version_info
    
    print(f"Current Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    
    # Check if Python version is 3.11.x
    if python_version.major == 3 and python_version.minor == 11:
        print("✅ Python version 3.11.x detected - Compatible with AWS App Runner")
    else:
        print(f"❌ Python version {python_version.major}.{python_version.minor}.{python_version.micro} detected")
        print("AWS App Runner requires Python 3.11.x for this application")
        print("Please update your apprunner.yaml file to use runtime: python3.11")

if __name__ == "__main__":
    main() 