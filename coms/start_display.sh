#!/bin/bash
ssh -T -X -n obs@corona "cd /home/corona/cactus/APA/display; ./tsd_client --geometry 864x487"
