FROM python:3.6
RUN mkdir /home/azurefs
WORKDIR /home/azurefs

# Copy relative folder
#COPY individual files
COPY *.py ./
COPY init.sh ./
COPY key.json ./
COPY keys.sh ./
RUN chmod +x init.sh
RUN chmod +x keys.sh


# ssh
ENV SSH_PASSWD "root:Docker!"
RUN apt-get update \
        && apt-get install -y --no-install-recommends dialog \
        && apt-get update \
    && apt-get install -y --no-install-recommends openssh-server \
    && echo "$SSH_PASSWD" | chpasswd 

COPY sshd_config /etc/ssh/

EXPOSE 8000 5000

ENV PATH="/home/detector/miniconda3/bin:${PATH}"

RUN apt-get update && apt-get install -y \
    curl

RUN pip install numpy 
RUN pip install azure-storage-file

# following command takes fairly long to execute, do I need this? docker im

ENTRYPOINT ["./init.sh"]
