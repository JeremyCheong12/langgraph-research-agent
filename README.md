# AI Research Agent (LangGraph)

A Python-based AI agent that researches topics using a Plan-Execute-Summarize workflow. It uses LangGraph for state management and Google Gemini (Free Tier) for reasoning.

## Features
* **Planning Node:** Breaks complex topics into step-by-step search queries.
* **Research Loop:** Iteratively executes searches using DuckDuckGo and Wikipedia.
* **State Management:** Maintains context and search logs across the entire session.
* **Fault Tolerance:** Handles tool failures/timeouts gracefully without crashing.

## Architecture
graph TD
    %% Nodes
    Start([Start]) --> Planner[Planner Node]
    Planner -->|"Generate Search Steps"| Worker[Worker Node]
    
    %% The Research Loop
    subgraph Research_Loop [Iterative Research Process]
        Worker -->|"Execute Top Step"| Tools{Select Tool}
        Tools -->|"Define/History"| Wiki[Wikipedia Tool]
        Tools -->|"General Query"| Web[DuckDuckGo Tool]
        
        Wiki --> Log[Log Result]
        Web --> Log
        
        Log --> Router{More Steps?}
    end
    
    %% Conditional Logic
    Router -- "Yes (Loop)" --> Worker
    Router -- "No (Done)" --> Writer[Writer Node]
    
    %% Final Output
    Writer -->|"Synthesize Answer"| End([End])
    
    %% Styling
    style Start fill:#f9f,stroke:#333,stroke-width:2px
    style End fill:#f9f,stroke:#333,stroke-width:2px
    style Planner fill:#bbf,stroke:#333
    style Worker fill:#bfb,stroke:#333
    style Writer fill:#bfb,stroke:#333

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