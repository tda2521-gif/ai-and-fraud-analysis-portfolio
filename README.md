# AI & Fraud Analysis Portfolio

## Project Overview
Brief description of your business problem and analytics solution.

## Business Problem
- What business challenge are you addressing?
- Why is this problem important?
- What impact will solving it have?

## Data Sources
- Description of data sources
- Data acquisition methods
- Data quality considerations

## Solution Architecture
- High-level system design
- Key components and their relationships
- Technology stack overview

## Setup Instructions

### Prerequisites
- Python 3.14+
- UV package manager
- Git

### Installation
1. Clone this repository:
   git clone <https://github.com/tda2521-gif/ai-and-fraud-analysis-portfolio.git>
   cd business-analytics-portfolio
   ```

2. Set up environment:
   uv sync

3. Run anything inside the project environment:
   uv run python scripts/run_pipeline.py
   
   UV resolves the environment for each command, so there is no separate activation step.
   If you prefer a traditional activated shell, use `source .venv/bin/activate` on macOS
   and Linux, or `.venv\Scripts\activate` on Windows.

### Usage
- Data pipeline: `uv run python scripts/run_pipeline.py`
- Analysis: `uv run jupyter notebook notebooks/`
- Dashboard: `uv run python src/dashboard/app.py`

## Project Structure
Brief explanation of folder organization and key files.

## Results
Summary of key findings and business impact.

## Future Work
Planned improvements and extensions.
