#!/bin/bash

# Add README.md to Dockerfile
echo "🔧 Adding README.md to Dockerfile..."

# Add README.md copy after pyproject.toml
sed -i '' '/COPY pyproject.toml \/app\//a\
COPY README.md /app/
' Dockerfile

echo "✅ Added README.md to Dockerfile"
echo "📋 Checking the updated Dockerfile:"
grep -A2 -B2 "README.md" Dockerfile
