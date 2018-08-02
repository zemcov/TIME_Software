#!/bin/bash
#RC = $1
ssh -T pilot2@timemce.rit.edu /usr/mce/bin/mce_cmd "-x stop rc$1 ret_dat"

