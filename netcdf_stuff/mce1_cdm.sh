#!/bin/bash
#RC = $1
#FRAME = $2
ssh -T pilot2@timemce.rit.edu /usr/mce/bin/mce_cmd "-x wb rc$1 data_mode $2"

