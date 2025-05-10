FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Add build argument for port
ARG PORT=8000
ENV PORT=${PORT}

# Copy dependency file and install packages
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the source code into the container
COPY . .

# Expose the port
EXPOSE ${PORT}

# Default command can be overridden by docker-compose
CMD ["python", "-m", "uvicorn", "main:app", "--host=0.0.0.0", "--port=${PORT}"]
