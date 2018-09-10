#!/bin/bash
CMD = $1
if [$CMD = 'start']; then
  ssh -T pilot2@timemce.rit.edu 'python /home/pilot2/TIME_Software/mce1_sftp.py'
fi

if [$CMD = 'stop']; then
  ssh -T pilot2@timemce.rit.edu 'pkill -f python /home/pilot2/TIME_Software/mce1_sftp.py'
fi
