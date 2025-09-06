#!/usr/bin/env python3
"""Fix build issues by updating pyproject.toml"""

def fix_pyproject():
    """Remove README.md requirement from pyproject.toml"""
    
    with open('pyproject.toml', 'r') as f:
        content = f.read()
    
    # Remove the readme line
    content = content.replace('readme = "README.md"\n', '')
    
    with open('pyproject.toml', 'w') as f:
        f.write(content)
    
    print("✅ Fixed pyproject.toml - removed README.md requirement")

if __name__ == "__main__":
    fix_pyproject()
