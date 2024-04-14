# Use the official Ubuntu 22.04 image as the base image
FROM ubuntu:22.04

# Update the package lists and install necessary packages
# RUN echo $(which apt)
# RUN echo $(which apt-get)

RUN apt-get update
RUN apt-get install -y python3.9 python3-distutils python3-pip

# Set the working directory in the container
WORKDIR /app

# Copy the local code to the container's working directory (if needed)
COPY . /app

# Install any Python dependencies using pip (if needed)
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose any necessary ports (if needed)
EXPOSE 5000

# Specify the command to run on container start (if needed)
CMD ["python3", "app.py"]
