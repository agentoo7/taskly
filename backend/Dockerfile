# Development Dockerfile for FastAPI with hot reload using UV
FROM python:3.11.7-slim

WORKDIR /app

# Install UV package manager
RUN pip install uv==0.1.18

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies using UV
RUN uv pip install --system -r pyproject.toml --all-extras

# Copy source code
COPY . .

# Expose port 8000
EXPOSE 8000

# Set Python to run in unbuffered mode for better logging
ENV PYTHONUNBUFFERED=1

# Start Uvicorn with hot reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
