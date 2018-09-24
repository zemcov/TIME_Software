#!/bin/bash
ssh -T pilot2@timemce.rit.edu /usr/mce/mce_script/script/mce_run "temp $1 $2 --sequence=$3"
