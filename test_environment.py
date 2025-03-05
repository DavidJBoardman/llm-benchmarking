#!/usr/bin/env python3
"""
Test script to verify the environment in AWS App Runner.
This script prints information about the environment and installed packages.
"""

import os
import sys
import platform
import pkg_resources

def main():
    print("=== Environment Information ===")
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Files in current directory: {os.listdir('.')}")
    
    print("\n=== Environment Variables ===")
    for key, value in os.environ.items():
        # Mask sensitive information
        if any(sensitive in key.lower() for sensitive in ['password', 'secret', 'key']):
            print(f"{key}: ***MASKED***")
        else:
            print(f"{key}: {value}")
    
    print("\n=== Installed Packages ===")
    for package in sorted([f"{pkg.key}=={pkg.version}" for pkg in pkg_resources.working_set]):
        print(package)

if __name__ == "__main__":
    main() 