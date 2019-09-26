#!/bin/bash
#RC = $1
ssh -T time@time-mce-0 /usr/mce/bin/mce_cmd "-x stop rc$1 ret_dat"
