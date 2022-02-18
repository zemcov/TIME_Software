#!/bin/bash
echo 'killing hk_sftp on time-hk ...'
sleep 1;
ssh time-hk 'echo "killing the following PIDs now:"; echo $(pgrep -f sftp)'
ssh time-hk 'kill $(pgrep -f sftp)'
echo 'an error should normally follow. if there is an actual ps entry then go kill -9 it!'
sleep 1;
ssh time-hk 'if [[ $(pgrep -f sftp) ]]; then ps -f $(pgrep -f sftp); else echo "no sftp processes"; fi'
sleep 1;
ssh time-mce-0.local 'kill $(pgrep -f rsync)'
echo 'two errors should normally follow. if there is an actual ps entry then go kill it!'
sleep 1;
ssh time-mce-0.local 'if [[ $(pgrep -f rsync) ]]; then ps -f $(pgrep rsync); else echo "no rsync processes"; fi'
ssh time-mce-0.local 'if [[ $(pgrep -f mce_cmd) ]]; then ps -f $(pgrep mce_cmd); else echo "no mce_cmd processes"; fi'
sleep 1;
ss -atp | grep 192.168.1.252
sleep 1;
echo 'we now attempt to kill any remaining processes that are talking to the telscope tracker.'
kill $(ss -atp | awk '/192.168.1.252/ {split($6,a,",");split(a[2],b,"=");print b[2]}')
sleep 1;
echo 'I think it is done. mind checking?'
ss -atp | grep 192.168.1.252
