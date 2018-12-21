conda list -e > req.txt
conda env export | grep -v "^prefix: " > environment.yml


# to create another file
conda env export > environment.yml