# Step 1: Base image with Python
FROM python:3.11-slim

# Step 2: Set working directory
WORKDIR /app

# Step 3: Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Step 4: Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy application code
COPY . .

# Step 6: Expose port
EXPOSE 8000

# Step 7: Run the API using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
