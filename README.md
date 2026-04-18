# Agent Systems Tryout

This repository contains the ASE project code copied from `Master/new/2ndsemster/ASE/Projekt`.

## Prerequisites

- Python 3.10+
- pip
- Optional: Ollama running locally (for `llama3.2` model usage)
- OpenAI API key (if you want to run OpenAI-backed agents)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables

Set your OpenAI key before running scripts that use `OpenAIChatCompletionClient`:

```bash
export OPENAI_API_KEY="<your-openai-key>"
```

Optional model/server configuration can be set depending on your local setup.

## Run

Typical entry points are under `AutoGen/`.

```bash
python AutoGen/group_agents.py
```

or

```bash
python AutoGen/solo_agent.py
```

## Notes

- Hardcoded API keys were removed intentionally; runtime configuration is required.
- If you use Ollama, ensure the target model is available locally.
