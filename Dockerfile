# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Copy entrypoint.sh script
COPY entrypoint.sh /entrypoint.sh

# Make entrypoint.sh executable
RUN chmod +x /entrypoint.sh

# Expose the port the app runs on
EXPOSE 8000

# Run the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
