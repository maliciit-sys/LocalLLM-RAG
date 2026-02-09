#!/bin/bash
echo "🚀 Starting LocalLLM-RAG..."
sudo systemctl start postgresql
sleep 1
cd ~/ml-projects/python-projects/LocalLLM-RAG
source ~/ml-projects/ml-env/bin/activate
python src/api/app.py
