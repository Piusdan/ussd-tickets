# Use an official Python runtime as a parent image
FROM python:2.7-slim

MAINTAINER Pius Dan Nyongesa <npiusdan@gmail.com>

# Set the working directory
WORKDIR /cashvalue-backend

# Copy the current directory contents into the container at /app
ADD . /cashvalue-backend



# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# create unprivileged user
RUN adduser --disabled-password --gecos '' cvs