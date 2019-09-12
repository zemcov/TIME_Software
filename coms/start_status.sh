#!/bin/bash
ssh -T -X -n obs@corona "cd /home/corona/cactus/status; ./status -n"
