#!/bin/bash
#mce = $1
ssh -T time@time-mce-$1 'pkill -f mce_rsync'
