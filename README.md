# hydra (alpha version)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)

A python package for the distributed simulation of urban water systems using flyte.

## Prerequisites

- Docker installed and running
- kubectl installed
- flytectl installed (`brew install flytectl`)
- uv installed (`pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Getting Started

### Setup Local Flyte Instance

1. Start a local Flyte cluster:
    ```bash
    flytectl demo start
    ```
    This will start a local Kubernetes cluster with Flyte installed.

2. Create a builder context:
    ```bash
    envd context create --name flyte-sandbox --builder tcp --builder-address localhost:30003 --use
    ```

### Register and Run Workflow

1. Install dependencies:
    ```bash
    uv sync
    ```

1. Run the workflow:
    ```bash
    uv run pyflyte run --remote example.py main --data '[0.5, 0.6, 0.7, 0.8, 10.0]'
    ```

You can monitor the workflow execution in the Flyte UI at http://localhost:30080/console

### Cleanup

To stop the local Flyte cluster:
    ```bash
    flytectl demo stop
    ```
