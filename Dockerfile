# Use official Python base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Start the app with Uvicorn inside the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
