# Agentic Content Transformation System
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![LangGraph](https://img.shields.io/badge/LangGraph-powered-green)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A high-precision content adaptation framework built with **LangGraph**. This system uses a specialized multi-agent workflow to rewrite text into different styles (e.g., Academic to Blog) while ensuring 100% factual accuracy through automated Quality Control (QC) loops.

## 🚀 Why This System?

Traditional LLM prompts often lose nuance or hallucinate facts during complex rewrites. This system solves that by:
1.  **Breaking down the task**: Separating analysis, planning, and execution.
2.  **RAG-Enhanced Logic**: Using a Knowledge Base to pull specific style guides and templates.
3.  **Self-Correction**: If the QC agent finds a factual error or style mismatch, it automatically triggers a re-transformation.

---

## 🧠 How It Works (The Pipeline)

The system operates as a state machine:

| Step | Agent | Responsibility |
| :--- | :--- | :--- |
| **1. Analyze** | `StyleAnalyst` | Detects tone, complexity, and audience of the source text. |
| **2. Plan** | `Planner` | Queries the **RAG Service** for style guidelines and formatting templates. |
| **3. Transform** | `Converter` | Performs the actual rewrite based on the generated plan. |
| **4. Verify** | `QC Agent` | Scores the output for factual consistency and style matching. |
| **5. Loop** | **Orchestrator** | If scores are low, sends the text back to Step 3 for refinement (up to 3 times). |

## 📂 Project Structure

```text
app/
├── agents/          # Brains: Logic for specialized AI agents
├── graph/           # Nervous System: Workflow definitions and state nodes
├── services/        # Tools: LLM wrappers, RAG retrieval, and fact-checkers
└── config/          # Settings: Prompts and environment variables
```

---

## 🛠️ Setup & Installation

### 1. Prerequisites
Ensure you have Python 3.9+ installed.

### 2. Install Dependencies
```bash
pip install fastapi uvicorn openai langgraph pydantic-settings langchain-openai slowapi loguru pyjwt python-dotenv prometheus-fastapi-instrumentator opentelemetry-instrumentation-fastapi
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_api_key_here
MODEL_NAME=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1  # Optional: change for custom endpoints
JWT_SECRET_KEY=your_jwt_secret_key_here # IMPORTANT: Change this in production!

# Observability (Tracing & Metrics)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT="content-transformation-system"

# OpenTelemetry (Optional: Export to Jaeger/OTLP)
OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
OTEL_SERVICE_NAME="agent-system"
```

---

## 🚀 Quick Start

You can trigger the entire agentic pipeline with a few lines of code:

```python
from app.graph.workflow import run_workflow

# 1. Define your transformation requirements
result = run_workflow(
    source_text="The implementation of the new API endpoint resulted in a 20% latency reduction.",
    target_style="blog",
    target_complexity="simple",
    target_format="markdown"
)

# 2. Review the output
print(f"Content: {result['transformed_content']}")
print(f"Quality Score: {result['quality_score']}/100")
```

## 🧪 Key Components Detail

- **RAG Service (`rag_service.py`)**: Currently holds a mock knowledge base of style guides (Academic, Professional, etc.). This is where you can plug in a real Vector Database like Pinecone or Chroma.
- **State Management (`state.py`)**: Tracks the content, metrics, and agent logs as the data flows through the graph.
- **Feedback Loop**: Defined in `graph.py`, it ensures the system doesn't settle for "good enough" if the fact-check score is below 90%.

---
