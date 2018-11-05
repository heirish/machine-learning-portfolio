#!/bin/bash
export KAGGLE_USERNAME=$1
export KAGGLE_KEY=$2
# competition_name=human-protein-atlas-image-classification
competition_name=$3

if [ $# -ne 3 ]; then
    echo "Usage:"
    echo -e "\t $0 kaggle_username kaggle_key competition_name"
    exit 1
fi

set -x 

echo "============================will download data for competition: $competition_name=============================="
echo '============================following files will be downloaded==========================='
kaggle competitions files $competition_name
kaggle competitions download $competition_name
