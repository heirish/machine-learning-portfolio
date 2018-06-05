#! /bin/bash
source activate py36
if [ $# -ne 3 ]
then
    echo Usage: ${0} year topics iterations
    exit 1
fi
nohup python TopicLDA.py --input_data_dir Data_in --output_data_dir Data_out  --year ${1} --topics ${2} --max_steps ${3} > Data_out/${1}.log &

