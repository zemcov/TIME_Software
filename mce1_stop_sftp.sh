
#!/bin/bash
ssh -T pilot2@timemce.rit.edu /usr/mce/bin/mce_cmd '-x stop rcs ret_dat'

kill $(pgrep -f 'python run.py')
ssh -T pilot2@timemce.rit.edu 'pkill -f mce1_sftp.py'

ssh -T pilot2@timemce.rit.edu 'rm /data/cryo/current_data/temp.*'

rm mce1/temp.*

kill $(pgrep -f 'python netcdf.py')
