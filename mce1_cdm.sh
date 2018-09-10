#!/bin/bash
RC = $1
FRAME = $2
ssh -T pilot2@timemce.rit.edu /usr/mce/bin/mce_cmd "-x wb rc$RC data_mode $FRAME"
