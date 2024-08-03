FROM ubuntu:22.04

# Set the working directory
WORKDIR /app

# Ensure apt is in non-interactive to avoid issues with some packages
ARG DEBIAN_FRONTEND=noninteractive

# Install necessary packages and dependencies
RUN apt-get update -o Acquire::Retries=3 && \
    apt-get install -y wget gnupg unzip -o Acquire::Retries=3 && \
    apt-get install -y libxss1 libappindicator3-1 libindicator7 fonts-liberation libnss3 xdg-utils \
                       libasound2 libcurl4 libgbm1 libu2f-udev libvulkan1 && \
    apt-get install -y python3 python3-pip && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb && \
    apt-get -f install -y && \  
    wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y postgresql postgresql-contrib postgresql-client python3-pip sudo

# Copy application code and install dependencies
COPY . /app
COPY requirements.txt /src/requirements.txt
RUN pip3 install --no-cache-dir -r /src/requirements.txt

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Make port 80 available to the world outside this container
EXPOSE 80

# Run main.py when the container launches
# CMD service postgresql start && python3 /app/src/main.py
ENTRYPOINT ["/app/entrypoint.sh"]
