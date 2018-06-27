#!/bin/bash
#!/bin/bash
CMD = $1
if [$CMD = 'start']; then
  ssh -T time@time-mce-0.caltech.edu 'python /home/time/rit-software/TIME_Software/mce2_sftp.py'
fi

if [$CMD = 'stop']; then
  ssh -T pilot2@time-mce-0.caltech.edu 'pkill -f python /home/time/rit-software/TIME_Software/mce2_sftp.py'
fi
