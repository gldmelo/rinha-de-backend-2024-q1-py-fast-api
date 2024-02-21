# Use the official Python image as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /src

# Copy the requirements.txt file into the container
COPY ./src/requirements.txt .

# Install dependencies
RUN python -m pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of your application code into the container
WORKDIR /src
COPY . /src

# Expose port 8000 (or the port your FastAPI app is running on)
EXPOSE 8000

# Command to run your FastAPI application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info", "--proxy-headers"]
