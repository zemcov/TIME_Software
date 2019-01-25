#!/bin/bash
#DR = $1
# this is for the mce computer...
ssh -T time-mce-0 /usr/mce/bin/mce_cmd "-x wb cc data_rate $1"
