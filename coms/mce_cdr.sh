#!/bin/bash
#mce = $1
#DR = $2
# this is for the mce computer...
ssh -T time@time-mce-$1 /usr/mce/bin/mce_cmd "-x wb cc data_rate $2"
