# IntelPulse

IntelPulse is a market analytics web application that provides machine-learning-assisted stock and forex trend predictions, technical indicators, news sentiment, and interactive price charts.

**Project repository:** [github.com/agrawalyash292007/IntelPulse](https://github.com/agrawalyash292007/IntelPulse)

**Live demo:** Add the Render URL after the first successful deployment (for example, `https://intelpulse.onrender.com`).

## Features

- Secure user registration and login with JWT authentication
- Trend predictions for equities, Indian stocks, and selected forex pairs
- Technical analysis using RSI, moving-average crossover signals, and volatility
- News sentiment scoring with NLTK VADER
- Interactive candlestick charts powered by TradingView Lightweight Charts
- Saved prediction history for authenticated users
- Database migrations with Alembic
- Dockerized local development and Render-ready cloud deployment

## Technology Stack

| Area | Technologies |
| --- | --- |
| Backend | Python, FastAPI, Pydantic, Uvicorn |
| Data and ML | pandas, NumPy, scikit-learn, joblib, yfinance, NLTK VADER |
| Database | SQLAlchemy (async), SQLite for local development, PostgreSQL for Render |
| Security | JWT, python-jose, bcrypt |
| Frontend | HTML, Tailwind CSS, TradingView Lightweight Charts |
| DevOps | Docker, Docker Compose, Alembic, GitHub Actions, Render |

## Run Locally with Docker

1. Create a `.env` file with a secure application secret:

   ```env
   SECRET_KEY=replace-with-a-long-random-secret
   ```

2. Build and start the application:

   ```bash
   docker compose up --build
   ```

3. Open the application at [http://localhost:8000](http://localhost:8000). The health endpoint is available at [http://localhost:8000/health](http://localhost:8000/health).

The local service is named `api`; its running Docker container is `intelpulse_backend`.

## Run Tests

```bash
SECRET_KEY=local_test_secret PYTHONPATH=. pytest -q
```

## Deploy to Render

The repository includes [`render.yaml`](render.yaml), which creates:

- a Docker-based Render web service;
- a managed PostgreSQL database;
- a generated `SECRET_KEY`;
- automatic database migrations at application startup.

To deploy, push this repository to GitHub, then in Render select **New → Blueprint** and choose the repository. Render detects `render.yaml`, builds the Docker image, and provisions the required services.

> Render free web services spin down after inactivity. Free Render Postgres databases are intended for demos and expire after 30 days.

## API Endpoints

| Endpoint | Description |
| --- | --- |
| `GET /health` | Service health status |
| `POST /api/v1/auth/signup` | Register a user |
| `POST /api/v1/auth/login` | Authenticate and receive a JWT |
| `POST /api/v1/analytics/analyze` | Run an authenticated market analysis |
| `GET /api/v1/analytics/chart` | Retrieve historical OHLC candle data |
| `GET /api/v1/analytics/history` | Retrieve the authenticated user's prediction history |
