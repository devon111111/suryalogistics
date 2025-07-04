FROM python:3.10-slim

# Set working directory to /app
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy only necessary files
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install python-multipart

# Copy your project inside Docker
COPY ./src /app

# Expose port (optional but good practice)
EXPOSE 8000

# Run FastAPI app using Railway-assigned PORT
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
