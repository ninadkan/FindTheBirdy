conda list -e > req.txt
conda env export | grep -v "^prefix: " > environment.yml