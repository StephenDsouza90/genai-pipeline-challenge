# Use an official Python runtime as a parent image
FROM python:3.13.3-slim

# Set the working directory in the container
WORKDIR /app

# Copy pyproject.toml first for dependency installation
COPY pyproject.toml ./

# Copy the rest of the application code into the container
COPY . .

# Install the dependencies and the package in editable mode
RUN pip install --no-cache-dir -e .

# Expose the port the app will run on
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]