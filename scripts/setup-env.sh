#!/bin/bash

# Setup environment files for Taskly
# This script copies example environment files to actual .env files

set -e

echo "Setting up environment files for Taskly..."

# Backend .env
if [ -f "backend/.env" ]; then
    echo "⚠️  backend/.env already exists. Skipping..."
else
    cp backend/.env.example backend/.env
    echo "✓ Created backend/.env from backend/.env.example"
fi

# Frontend .env.local
if [ -f "frontend/.env.local" ]; then
    echo "⚠️  frontend/.env.local already exists. Skipping..."
else
    cp frontend/.env.local.example frontend/.env.local
    echo "✓ Created frontend/.env.local from frontend/.env.local.example"
fi

echo ""
echo "Environment files created successfully!"
echo ""
echo "⚠️  IMPORTANT: Update the following values in your .env files:"
echo "   - backend/.env: SECRET_KEY, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET"
echo "   - frontend/.env.local: NEXT_PUBLIC_GITHUB_CLIENT_ID"
echo ""
echo "To create a GitHub OAuth app:"
echo "   1. Go to https://github.com/settings/developers"
echo "   2. Click 'New OAuth App'"
echo "   3. Set Authorization callback URL to: http://localhost:3000/auth/callback"
echo "   4. Copy the Client ID and Client Secret to your .env files"
