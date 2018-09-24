#!/bin/bash
#CMD = $1
echo $1
if [ "$1" = "start" ]
then
  ssh -T pilot1@time.rit.edu 'python /home/pilot1/TIME_Software/tel_sock.py'
  echo 'Started'
fi

if [ "$1" = "stop" ]
then
  ssh -T pilot1@time.rit.edu pkill python
  echo 'Stopped'
fi
