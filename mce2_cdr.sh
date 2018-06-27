#!/bin/bash
DR = $1
ssh -T time@time-mce-0.caltech.edu /usr/mce/bin/mce_cmd "-x wb cc data_rate $DR"
