# Use an official Python runtime as a parent image
FROM python:3.12.0

# Setup environment variable
ENV DockerHOME=/Django_REST_Image_Uploader

# Set working directory
WORKDIR $DockerHOME

# The environment variable ensures that the Python output is not buffered
ENV PYTHONUNBUFFERED 1

# Install dependencies (separate COPY and pip install for caching)
COPY requirements.txt $DockerHOME/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project to the Docker home directory
COPY . $DockerHOME

# Expose the port your application will run on
EXPOSE 9000

# Define the command to run your application
CMD python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:9000
