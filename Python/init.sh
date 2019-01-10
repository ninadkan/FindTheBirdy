#!/bin/bash
source activate
source keys.sh
#as is the norm of the shell script, please make sure that there is no space between the variable being declared and the 
#allocation. for e.g. 
# following will error 
# execCmdLineValue = "python docker_clsOpenCVProcessImages.py -v processImages"
# and the next statement willnot error
# This script does a mapping between environment variables specified on the command lines and those expected by the 
# python script. if those are changed, then this file will need to be editied. 
e0="python docker_clsOpenCVProcessImages.py -v processImages "
echo ${e0}
# if ! [[ -z "${EXPERIMENT_NAME}" ]]; then
#     e1="${e0} -exn=${EXPERIMENT_NAME} "
#     echo ${e1}
#     ${e1}
#     if ! [[ -z "${OFFSET}" ]]; then
#         e2="${e1} -oft=${OFFSET} "
#         echo ${e2}
#         ${e2}
#         if ! [[ -z "${BATCH_SIZE}" ]]; then
#             e3="${e2} -bsz=${BATCH_SIZE} "
#             echo ${e3}
#             ${e3}
#             if ! [[ -z "${NUM_IMAGES}" ]]; then
#                 e4="${e3} -nip=${NUM_IMAGES} "
#                 echo ${e4}
#                 ${e4}
#                 if ! [[ -z "${SRC_FOLDER}" ]]; then
#                     e5="${e4}  -sif=${SRC_FOLDER} "
#                     echo ${e5}
#                     ${e5}
#                     if ! [[ -z "${DEST_FOLDER}" ]]; then
#                         e6="${e5}  -dif=${DEST_FOLDER} "
#                         echo ${e6}
#                         ${e6}
#                         if ! [[ -z "${FILENAME_EXT}" ]]; then
#                             e7="${e6} -fnx=${FILENAME_EXT} "
#                             echo ${e7}
#                             ${e7}
#                             if ! [[ -z "${PART_OF_FILE_NAME}" ]]; then
#                                 e8="${e7}  -pfn=${PART_OF_FILE_NAME} "
#                                 echo ${e8}
#                                 ${e8}
#                             fi
#                         fi
#                     fi
#                 fi
#             fi
#         fi
#     fi
# fi


if ! [[ -z "${EXPERIMENT_NAME}" ]]; then
   e1=" -exn=${EXPERIMENT_NAME} "
fi

if ! [[ -z "${OFFSET}" ]]; then
    e2=" -oft=${OFFSET} "
fi

if ! [[ -z "${BATCH_SIZE}" ]]; then
    e3=" -bsz=${BATCH_SIZE} "
fi

if ! [[ -z "${NUM_IMAGES}" ]]; then
    e4=" -nip=${NUM_IMAGES} "
fi

if ! [[ -z "${SRC_FOLDER}" ]]; then
    e5=" -sif=${SRC_FOLDER} "
fi

if ! [[ -z "${DEST_FOLDER}" ]]; then
    e6=" -dif=${DEST_FOLDER} "
fi

if ! [[ -z "${FILENAME_EXT}" ]]; then
    e7=" -fnx=${FILENAME_EXT} "
fi

if ! [[ -z "${PART_OF_FILE_NAME}" ]]; then
    e8=" -pfn=${PART_OF_FILE_NAME} "
fi


echo ${e1}
echo ${e2}
echo ${e3}
echo ${e4}
echo ${e5}
echo ${e6}
echo ${e7}
echo ${e8}

eFinal="${e0}${e1}${e2}${e3}${e4}${e5}${e6}${e7}${e8}"
echo ${eFinal}
# Finally execute
${eFinal}
