#!/bin/bash

# Quick fix for Dockerfile backslash issues
echo "🔧 Fixing Dockerfile..."

# Replace double backslashes with single backslashes
sed -i '' 's/\\\\/\\/g' Dockerfile

echo "✅ Fixed Dockerfile backslashes"
echo "📋 Checking the fixed lines:"
grep -n "\\\\" Dockerfile || echo "No double backslashes found - good!"
