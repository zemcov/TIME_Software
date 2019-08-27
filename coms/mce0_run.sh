#!/bin/bash
#RC = $2
#FRAME = $1
#NUM = $3
ssh -T time@time-mce-0 /usr/mce/mce_script/script/mce_run "temp $1 $2 --sequence=$3"
