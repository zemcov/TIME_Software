#!/bin/sh
/usr/bin/rsync -a --no-links --delete /usr/local/share/moin /media/pilot1/external/ >> /tmp/timewiki_backup.log 2>&1 /
cat /tmp/timewiki_backup.log >> /var/log/crond/timewiki_backup.log /
rm /tmp/timewiki_backup.log /
