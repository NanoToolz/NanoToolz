# ============================================
# DOCKERFILE - Bot Container
# ============================================

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot files
COPY . .

# Run bot
CMD ["python", "main.py"]
