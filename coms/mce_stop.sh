#!/bin/bash
#mce = $1
#RC = $2
ssh -T time@time-mce-$1 /usr/mce/bin/mce_cmd "-x stop rc$2 ret_dat"
