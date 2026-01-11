# ML Fraud Detection API

This project implements a REST API for detecting fraudulent credit card transactions using machine learning. Built with FastAPI, it provides asynchronous endpoints for real-time transaction scoring. The system uses a pre-trained model to evaluate transaction features and return fraud probabilities and decisions.

## Problem Solved

Credit card fraud detection is critical for financial institutions, with significant economic impact. This API addresses the need for automated, real-time fraud assessment by analyzing transaction data such as amount, time, merchant category, and user behavior patterns. It outputs a fraud probability score and a binary decision (fraudulent or legitimate), enabling integration into payment processing workflows.

## Principles Applied

The architecture follows clean code principles with clear separation of concerns. The API layer handles HTTP requests, validation, and responses, while the machine learning components are isolated for easy maintenance and updates. Technologies include FastAPI for high-performance web services, SQLAlchemy for database ORM, and Pydantic for data validation. Comprehensive unit testing with mocked dependencies ensures reliability. Containerization with Docker facilitates deployment and scalability.

## Project Structure

The codebase is organized as follows:

- **app/**: Core application code.
  - **routers/**: API endpoints. `score.py` manages fraud scoring, `transactions.py` handles transaction retrieval, and `items.py` provides basic CRUD operations.
  - **services/**: Business logic layer, including scoring services.
  - **models/**: SQLAlchemy database models for transactions, predictions, and items.
  - **schemas/**: Pydantic schemas for request and response validation.
  - **core/**: Model management, including loading and threshold configuration.
  - **utils/**: Utility functions for logging and common operations.
  - **main.py**: FastAPI application initialization and routing.

- **tests/**: Unit tests for routers, using mocks to avoid external dependencies.

- **docker/**: Docker Compose configuration for containerized deployment with PostgreSQL.

- **scripts/**: Data import scripts for populating the database.

- **artifacts/**: Pre-trained model files (e.g., joblib format).

- **resources/**: Sample datasets, such as transaction CSV files.

Separation of concerns is maintained: the API endpoints in `routers/` invoke model functions from `core/model_loader.py`, ensuring the web layer remains agnostic to model implementation details. This allows for model updates without API changes.

## How to Run

### Using Docker

Ensure Docker and Docker Compose are installed. Execute:

```bash
cd /workspace
docker-compose -f docker/docker-compose.yml up --build
```

This launches the API on port 8000 with a PostgreSQL database. API documentation is available at http://localhost:8000.

### Local Development

Requirements: Python 3.11+, PostgreSQL, and environment variables configured (see .env.sample).

1. Install dependencies: `pip install -r requirements.txt -r dev-requirements.txt`
2. Configure database and initialize tables (handled by SQLAlchemy on startup).
3. Start the application: `uvicorn app.main:app --reload`
4. Run tests: `pytest`

By default, a trained model is provided in `artifacts/` as a .joblib file. You can set a different path for a different model using the MODEL_PATH environment variable. The model must be a scikit-learn compatible model with `predict_proba` method.

### Using Devcontainers

For a consistent development environment, this project includes Devcontainer configurations. Devcontainers provide a fully configured development environment using Docker containers.

- **With Visual Studio Code**: Install the "Dev Containers" extension and reopen the project in a container. This automatically sets up the environment with all dependencies.

- **Standalone with Docker**: If you prefer not to use Devcontainers from Visual Studio Code, you can run the devcontainer standalone using Docker Compose. Execute:

  ```bash
  docker-compose -f .devcontainer/docker-compose.devcontainer.yml up --build
  ```

  This launches the development environment in a container with all dependencies configured.

## Next Steps

Future enhancements could include authentication mechanisms, rate limiting, and batch processing capabilities. Model performance monitoring and alerting should be integrated. Exploring advanced algorithms, such as deep learning models, could improve accuracy. Provide detailed documentation on training and updating the model. Production deployment considerations include Kubernetes orchestration and cloud services like AWS or GCP.