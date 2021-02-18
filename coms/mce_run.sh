#!/bin/bash
#mce = $1
#FRAME = $2
#RC = $3
#NUM = $4
ssh -T time@time-mce-$1 /usr/mce/mce_script/script/mce_run "temp $2 $3 --sequence=$4"
