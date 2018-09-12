#!/bin/bash
ssh -T time@time-mce-1.caltech.edu /usr/mce/bin/mce_cmd '-x stop rcs ret_dat'

kill $(pgrep -f 'python run.py')
ssh -T time@time-mce-1.caltech.edu 'pkill -f mce1_sftp.py'

ssh -T time@time-mce-1.caltech.edu 'rm /data/cryo/current_data/temp.*'

rm mce1/temp.*

kill $(pgrep -f 'python netcdf.py')
