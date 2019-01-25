#!/bin/bash
#RC = $1
ssh -T time-mce-0 /usr/mce/bin/mce_cmd "-x stop rc$1 ret_dat"
