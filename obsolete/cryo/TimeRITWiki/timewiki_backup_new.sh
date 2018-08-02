#!/bin/sh
/usr/bin/rsync -vrPeR /usr/local/share/moin /media/pilot1/62665E397FD17984 >> /tmp/timewiki_backup.log 2>&1
cat /tmp/timewiki_backup.log >> /var/log/crond/timewiki_backup.log
rm /tmp/timewiki_backup.log
