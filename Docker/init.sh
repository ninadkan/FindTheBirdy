#as is the norm of the shell script, please make sure that there is no space between the variable being declared and the 
#allocation. for e.g. 
# following will error 
# execCmdLineValue = "python docker_clsOpenCVProcessImages.py -v processImages"
# and the next statement willnot error
e0="python docker_clsOpenCVProcessImages.py -v processImages "
if ! [[ -z "${EXPERIMENT_NAME}" ]]; then
    e1="${e0} -exn=${EXPERIMENT_NAME} "
    if ! [[ -z "${OFFSET}" ]]; then
        e2="${e1} -oft=${OFFSET} "
        if ! [[ -z "${BATCH_SIZE}" ]]; then
            e3="${e2} -bsz=${BATCH_SIZE} "
            if ! [[ -z "${NUM_IMAGES}" ]]; then
                e4="${e3} -nip=${NUM_IMAGES} "
                if ! [[ -z "${SRC_FOLDER}" ]]; then
                    e5="${e4}  -sif=${SRC_FOLDER} "
                    if ! [[ -z "${DEST_FOLDER}" ]]; then
                        e6="${e5}  -dif=${DEST_FOLDER} "
                        if ! [[ -z "${FILENAME_EXT}" ]]; then
                            e7="${e6} -fnx=${FILENAME_EXT} "
                            if ! [[ -z "${PART_OF_FILE_NAME}" ]]; then
                                e8="${e7}  -pfn=${PART_OF_FILE_NAME} "
                            fi
                        fi
                    fi
                fi
            fi
        fi
    fi
fi
echo ${e8}
echo ${e7}
echo ${e6}
echo ${e5}
echo ${e4}
echo ${e3}
echo ${e2}
echo ${e1}
echo ${e0}
#execute
#$execCmdLineValue