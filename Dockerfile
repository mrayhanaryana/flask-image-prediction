# FROM python:3.8-slim-buster

# WORKDIR /python-docker

# COPY requirements.txt requirements.txt
# RUN pip3 install -r requirements.txt

# COPY . .

# CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
# Use an official Python runtime as the base image
FROM python:3.10.0

# Set the working directory in the container
WORKDIR /python-docker

# Copy the requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip3 install flask tensorflow pillow opencv-python google-api-python-client google-auth-httplib2 google-auth-oauthlib
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Copy the entire project to the working directory in the container
COPY . .

# Expose the Flask application's port (default is 5000)
EXPOSE 5000

# Set the command to run the Flask application
CMD ["flask", "run", "--host=0.0.0.0", "--reload"]
