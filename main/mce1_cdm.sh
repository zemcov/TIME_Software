#!/bin/bash
#RC = $1
#FRAME = $2
ssh -T time-mce-1 /usr/mce/bin/mce_cmd "-x wb rc$1 data_mode $2"
