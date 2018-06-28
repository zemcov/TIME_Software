#!/bin/bash
RC = $1
FRAME = $2
NUM = $3
ssh -T time@time-mce-0.caltech.edu /usr/mce/mce_script/script/mce_run "temp $FRAME $RC --sequence=$NUM"
