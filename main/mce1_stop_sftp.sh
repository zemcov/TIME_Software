#!/bin/bash
ssh -T time@time-mce-1.caltech.edu 'pkill -f mce1_sftp.py'

ssh -T time@time-mce-1.caltech.edu 'rm /data/cryo/current_data/temp.*'
