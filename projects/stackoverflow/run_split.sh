#! /bin/bash

source activate py36
python getAllTags.py > Data_out/exclude_tags_id.log  
python SplitInYear.py > Data_out/split.log
