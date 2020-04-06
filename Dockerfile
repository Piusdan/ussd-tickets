# Use an official Python runtime as a parent image
FROM darklotus/cvs-base:latest

MAINTAINER Pius Dan Nyongesa <npiusdan@gmail.com>

# Set the working directory
WORKDIR /opt/app

# Copy the current directory contents into the container at /app
ADD . .

# install additional packges for build

# Install any needed packages specified in requirements.txt
RUN /appenv/bin/pip install -r requirements.txt

# create unprivileged user
RUN adduser --disabled-password --gecos '' cvs

ENTRYPOINT [ "sh" ]