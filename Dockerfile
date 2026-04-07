FROM python:3.11-slim

WORKDIR /app

# Install build dependencies
RUN pip install --no-cache-dir setuptools wheel

# Copy only the files needed for installation first to leverage cache
COPY pyproject.toml README.md ./
COPY server/ ./server/
COPY env/ ./env/
COPY tasks/ ./tasks/

# Install the project and its dependencies
RUN pip install --no-cache-dir .

# Copy everything else
COPY . .

# Expose the default HF Spaces port
EXPOSE 7860

# Run the FastAPI server using the module path
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
