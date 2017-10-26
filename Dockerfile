# Use an official Python runtime as a parent image
FROM python:2.7-slim

MAINTAINER Pius Dan Nyongesa <npiusdan@gmail.com>

apt-get install wkhtmltopdf
apt-get install xvfb
echo -e '#!/bin/bash\nxvfb-run -a --server-args="-screen 0, 1024x768x24" /usr/bin/wkhtmltopdf -q $*' > /usr/bin/wkhtmltopdf.sh
chmod a+x /usr/bin/wkhtmltopdf.sh
ln -s /usr/bin/wkhtmltopdf.sh /usr/local/bin/wkhtmltopdf

# Set the working directory
WORKDIR /cashvalue-backend

# Copy the current directory contents into the container at /app
ADD . /cashvalue-backend



# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# create unprivileged user
RUN adduser --disabled-password --gecos '' cvs