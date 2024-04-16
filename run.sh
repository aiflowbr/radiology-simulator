#!/bin/sh

# . ./.env
# export DATASETPATH DATASET SUBDIR_IMAGES_PATTERN INTERVAL MODALITY BODY_REGION
# export AETITLE ADDRESS AEPORT REMOTE_AETITLE REMOTE_ADDRESS REMOTE_PORT
# python src/run.py

# docker run --rm -it -v /Users/anderson/Dev/MDCC/archive/CHEST_XRAY:/dataset --env-file=.env andersonbr/radiology-simulator python run.py
if [ "`uname`" == "Darwin" ]; then
    LOCAL_DATASET_PATH=/Users/anderson/Dev/MDCC/archive/CHEST_XRAY docker-compose up
else
    LOCAL_DATASET_PATH=/home/anderson/Dev/MDCC/chest_xray docker-compose up
fi
