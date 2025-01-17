# FastAPI Service Template

## Requirements

- [Docker](https://www.docker.com/) to containerize the app.
- [uv](https://docs.astral.sh/uv/) for Python package and environment management.

## Workflow

#### Dependencies are managed with **uv**.

Install it by running:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Once installed, you can run to sync & install dependencies:

```bash
uv sync
```

You can activate the virtual environment with:

```bash
source .venv/bin/activate
```

Finally, activate **pre-commit**:

```bash
pre-commit install
```

### Without docker

Run API with:

```bash
fastapi dev --reload app/main.py
```

### With docker

Start the local stack with Docker Compose (API + Postgres):

```bash
docker compose watch
```

#### Now you can interact with the API:

- JSON based web API based on OpenAPI: http://localhost:8000

- Automatic interactive documentation with Swagger UI: http://localhost:8000/docs

- Postgres db: http://localhost:5440

#### To check the logs, run (in another terminal):

```bash
docker compose logs
```

## Environment variables

The `.env` file contains all the configuration data.

Each environment variable is set up in the `.env` file for dev, but to let it prepared for our CI/CD system, the `docker-compose.yml` file is set up to read each specific env var instead of reading the `.env` file.

## Pre-commits, code linting & code formatting

We are using a tool called [pre-commit](https://pre-commit.com/) for code linting and formatting.

It runs right before making a commit in git. This way it ensures that the code is consistent and formatted even before it is committed.

You can find a file `.pre-commit-config.yaml` with configurations at the root of the project.

**To lint manually:**

```bash
bash scripts/lint.sh
```

**To format code manually:**

```bash
bash scripts/format.sh
```

## Test Coverage

When the tests are run, a file **htmlcov/index.html** is generated, you can open it in your browser to see the coverage of the tests.

To run test manually:

```bash
bash scripts/test.sh
```

## VS Code compatibility

There are already configurations in place to run the backend through the VS Code debugger, so that you can use breakpoints, pause and explore variables, etc. File with config located at `.vscode/launch.json`. If this repo is in within a workspace, move this config to the workspace root.

The setup is also already configured at `.vscode/settings.json` so you can run the tests through the VS Code Python tests tab.

## Links

- https://fastapi.tiangolo.com/tutorial/bigger-applications/
- https://docs.astral.sh/uv/
- https://pre-commit.com/
