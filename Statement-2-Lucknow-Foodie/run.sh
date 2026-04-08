#!/bin/bash
# ============================================
# Gourmet Guide — Startup Script
# RAG-Powered Lucknow Food Recommender
# ============================================

set -e

echo ""
echo "🍽️  GOURMET GUIDE — IIIT Lucknow Culinary Concierge"
echo "     Powered by RAG + FAISS + Google Gemini"
echo "=================================================="
echo ""

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BASE_DIR"

# Check for .env file
if [ -f ".env" ]; then
    echo "✅ Found .env file"
    export $(grep -v '^#' .env | xargs)
else
    echo "⚠️  No .env file found — running in retrieval-only mode"
    echo "   (Create .env with GEMINI_API_KEY for AI-powered responses)"
    echo ""
fi

# Check if vector DB exists, if not run ingest
if [ ! -f "vector_db/restaurants.faiss" ]; then
    echo "📊 Vector database not found. Building it now..."
    python3 src/ingest.py
    echo ""
else
    echo "✅ Vector database ready ($(python3 -c "import pickle; d=pickle.load(open('vector_db/restaurants_meta.pkl','rb')); print(len(d))") restaurants)"
fi

echo ""
echo "🚀 Starting server at http://localhost:8000"
echo "   Press Ctrl+C to stop"
echo ""

python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
