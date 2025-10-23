#!/usr/bin/env bash

# Database Reset Script
# WARNING: This script will DELETE ALL data in the database!

set -e

echo "⚠️  WARNING: This will DELETE ALL data in the database."
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "❌ Reset cancelled."
    exit 1
fi

echo "🗑️  Dropping all tables (alembic downgrade base)..."
alembic downgrade base

echo "🏗️  Recreating schema (alembic upgrade head)..."
alembic upgrade head

echo "🌱 Seeding database with test data..."
python -m scripts.seed_dev_data

echo "✅ Database reset complete!"
