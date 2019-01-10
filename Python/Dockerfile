FROM ubuntu:16.04
RUN useradd -ms /bin/bash detector
# I believe #D is for disabled password
# Nope, it complains and then bombs out saying -d option is ambiguous 
# RUN adduser -D detector
WORKDIR /home/detector

# Copy relative folder
COPY mobileNet mobileNet
COPY yolo yolo
COPY azureFS azureFS
COPY cosmosDB cosmosDB
#COPY individual files
COPY *.py ./
COPY init.sh ./
COPY keys/key.json ./
COPY keys/keys.sh ./
RUN chmod +x init.sh
RUN chmod +x keys.sh


ENV PATH="/home/detector/miniconda3/bin:${PATH}"

RUN apt-get update && apt-get install -y \
    bzip2\ 
    curl

# download miniconda
RUN curl -O https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh 
RUN chmod +x ./Miniconda3-latest-Linux-x86_64.sh

# install Miniconda on the given path and in silent mode
RUN ./Miniconda3-latest-Linux-x86_64.sh -b -p /home/detector/miniconda3

# python installation

RUN /bin/bash -c "source activate"
RUN conda install numpy 
RUN conda install -c conda-forge opencv
RUN pip install azure-storage-file

# following command takes fairly long to execute, do I need this? docker im
RUN chown -R detector:detector ./
USER detector

ENTRYPOINT ["./init.sh"]
