rem conda create --name pyflask python=3.6.6
conda list -n pyflask --no-show-channel-urls -e > requirements.txt
rem conda activate pyflask
conda list --export > objdetector.yml
# To create the environment
rem can install gunicorn under the conda environment
rem can start the gunicorn from the shell file created under the azureFS/ folder
rem conda env create -f objdetector.yml
rem install supervisor using 
rem apt-get install supervisor
rem next copy the docker/birdDetector.conf file to the /etc/supervisor/conf.d/ folder
rem sudo service supervisor start
rem test that both web service is working using the shell filer under /azureFS folder
/home/ninadk/BirdDetector/Python/docker/keys/keys.sh
