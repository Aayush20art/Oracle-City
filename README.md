# 🌆 Oracle City AI

Oracle City AI is an intelligent city assistant built using Streamlit, Mistral AI, OpenWeather API, and Tavily Search. It provides real-time weather updates and the latest city news through an agentic AI workflow with optional human-in-the-loop approval for tool execution.

## 🚀 Live Demo

**Application:** https://oracle-city-zkrvas8gnbbravvfcmssqb.streamlit.app/

**GitHub Repository:** https://github.com/Aayush20art/Oracle-City

---

## ✨ Features

### 🌦 Real-Time Weather Intelligence

* Fetches live weather data using OpenWeather API
* Displays temperature, humidity, wind speed, and weather conditions
* Supports Indian cities

### 📰 Latest News Retrieval

* Retrieves current city-related news using Tavily Search
* Provides summarized news results with source links
* Delivers real-time updates

### 🤖 Mistral AI Agent

* Powered by Mistral Large Language Model
* Understands natural language queries
* Automatically decides when tools should be used

### ⚡ Human Approval Workflow

* Human-in-the-loop architecture
* Approve or deny tool execution before API calls
* Increased transparency and control

### 🎨 Modern UI/UX

* Cyberpunk-inspired design
* Glassmorphism and neon effects
* Responsive Streamlit interface
* Interactive chat experience

### 🔧 Tool Calling System

* Weather Tool
* News Tool
* Agentic reasoning workflow
* Multi-step tool execution support

---

## 🏗️ Architecture

User Query
↓
Mistral AI Agent
↓
Tool Selection
↓
Human Approval (Optional)
↓
Weather API / News API
↓
AI Response Generation
↓
User Interface

---

## 🛠️ Tech Stack

### Frontend

* Streamlit
* Custom CSS
* Responsive UI Components

### AI & Agent Framework

* Mistral AI
* LangChain
* Tool Calling Architecture

### APIs

* OpenWeather API
* Tavily Search API

### Programming Language

* Python 3.11+

---

## 📦 Installation

### Clone Repository

```bash
git clone https://github.com/Aayush20art/Oracle-City.git
cd Oracle-City
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows

```bash
venv\Scripts\activate
```

Mac/Linux

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.streamlit/secrets.toml` file:

```toml
MISTRAL_API_KEY = "your_mistral_api_key"
OPENWEATHER_API_KEY = "your_openweather_api_key"
TAVILY_API_KEY = "your_tavily_api_key"
```

---

## ▶️ Run Locally

```bash
streamlit run app.py
```

---

## 💡 Example Queries

* What's the weather in Mumbai?
* Latest news from Delhi
* Weather and news for Hyderabad
* How's the weather in Chandigarh?
* Any breaking news in Bangalore?

---

## 📊 Key Highlights

* Agentic AI Workflow
* Real-Time Data Retrieval
* Human-in-the-Loop Approval
* Mistral AI Integration
* Tool Calling Architecture
* Streamlit Deployment
* Modern Interactive Interface

---

## 🎯 Learning Outcomes

This project demonstrates:

* Agentic AI Systems
* LLM Tool Calling
* Human Approval Workflows
* API Integration
* Streamlit Deployment
* Prompt Engineering
* LangChain Integration
* Real-Time Information Retrieval

---

## 📸 Project Preview

Visit the live application:

https://oracle-city-zkrvas8gnbbravvfcmssqb.streamlit.app/

---

## 👨‍💻 Author

**Aayush Sharma**

B.Tech Graduate | AI & Machine Learning Enthusiast

GitHub:
https://github.com/Aayush20art

---

## ⭐ Support

If you found this project useful, consider giving the repository a star ⭐ on GitHub.
