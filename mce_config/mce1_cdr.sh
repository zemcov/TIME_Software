#!/bin/bash
#DR = $1
# this is for the mce computer...
ssh -T time@time-mce-1.caltech.edu /usr/mce/bin/mce_cmd "-x wb cc data_rate $1"
