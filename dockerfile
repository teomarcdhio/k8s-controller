FROM python

# Set the working directory in the container
WORKDIR /app

# Copy the Python script into the container
COPY labelPodsController.py .

# Install required dependencies
RUN pip install kubernetes

# Run the Python script
CMD ["python", "labelPodsController.py"]