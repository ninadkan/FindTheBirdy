rem conda create --name pyflask python=3.6.6
conda list --no-show-channel-urls -e > requirements.txt
rem conda activate pyflask
conda list --export > objdetector.yml
# To create the environment
rem conda env create -f objdetector.yml
