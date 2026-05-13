# 🤖 Smart AI Business Assistant

An AI-powered business assistant platform for SMEs built with Groq LLM, RAG, Multi-Agent System, and Analytics Dashboard.

## ✨ Features
- 💬 AI Chat Assistant - Powered by Groq LLM (Llama 3.1)
- 📄 RAG System - Upload documents, get accurate answers
- 👥 Lead Management - Auto capture and classify Hot/Warm/Cold leads
- ⚡ Automations - Email summarizer, Lead reports, Bulk follow-ups
- 🤖 Multi-Agent System - Planner, Executor, Validator agents
- 📊 Analytics Dashboard - Visual charts and lead tracking

## 🛠️ Tech Stack
- Frontend: Streamlit
- LLM: Groq API (Llama 3.1 8B) - Free
- Vector DB: ChromaDB - Free
- Embeddings: Sentence Transformers - Free
- Language: Python 3.11+

## 🚀 Installation

### Step 1: Clone the repo
git clone https://github.com/Mnkp123/smart-ai-assistant.git
cd smart-ai-assistant

### Step 2: Create virtual environment
python -m venv venv
venv\Scripts\activate

### Step 3: Install dependencies
pip install -r requirements.txt

### Step 4: Create .env file
GROQ_API_KEY=your_groq_api_key_here
Get free key at: https://console.groq.com

### Step 5: Run the app
streamlit run app.py

Open: http://localhost:8501

## 📁 Project Structure
- app.py - Main Streamlit application
- chat_engine.py - Groq LLM integration
- rag_system.py - RAG with ChromaDB
- lead_manager.py - Lead capture and classification
- agents.py - Multi-agent system (Planner, Executor, Validator)
- config.py - Configuration and environment variables

## 🎯 Architecture
User Message → Planner Agent → Executor Agent → Validator Agent → Response + Auto Lead Capture

## 📊 Pages
- Chat Assistant - AI business chat
- Lead Management - View and manage leads
- Document Upload - Upload business documents
- Automations - Email and report automation
- Dashboard - Analytics and charts
- Logs - System activity logs