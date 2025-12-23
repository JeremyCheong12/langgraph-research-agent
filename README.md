# AI Research Agent (LangGraph)

A Python-based AI agent that researches topics using a Plan-Execute-Summarize workflow. It uses LangGraph for state management and Google Gemini (Free Tier) for reasoning.

## Features
* **Planning Node:** Breaks complex topics into step-by-step search queries.
* **Research Loop:** Iteratively executes searches using DuckDuckGo and Wikipedia.
* **State Management:** Maintains context and search logs across the entire session.
* **Fault Tolerance:** Handles tool failures/timeouts gracefully without crashing.

## Architecture
`Planner` -> `Researcher (Loop)` -> `Summarizer` -> `End`

## Setup

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/research-agent.git](https://github.com/YOUR_USERNAME/research-agent.git)
    cd research-agent
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set API Key**
    Open `main.py` and paste your Google Gemini API Key in line 14:
    ```python
    os.environ["GOOGLE_API_KEY"] = "AIzaSyD-..."
    ```

4.  **Run**
    ```bash
    python main.py
    ```