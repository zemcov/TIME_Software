#!/bin/bash
#RC = $1
ssh -T time@time-mce-1.caltech.edu /usr/mce/bin/mce_cmd "-x stop rc$1 ret_dat"
