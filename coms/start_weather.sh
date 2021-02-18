#!/bin/bash
ssh -T -X -n obs@modelo "cd /home/corona/cactus/weather; ./weather"
