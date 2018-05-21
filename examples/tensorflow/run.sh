#!/bin/bash
pip show tensorflow
python tf_example.py --input_data_dir ./data_input --log_dir ./data_output --max_steps 100
