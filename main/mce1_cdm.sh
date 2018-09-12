#!/bin/bash
#RC = $1
#FRAME = $2
ssh -T time@time-mce-1.caltech.edu /usr/mce/bin/mce_cmd "-x wb rc$1 data_mode $2"
