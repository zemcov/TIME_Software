#!/bin/bash
#mce = $1
#RC = $2
#FRAME = $3
ssh -T time@time-mce-$1 /usr/mce/bin/mce_cmd "-x wb rc$2 data_mode $3"
