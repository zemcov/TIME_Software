#!/bin/sh
/usr/bin/rsync -a --delete /usr/local/share/moin /run/media/zemcov/a1c02a0a-870a-419f-907f-8f3def5d12b7/ >> /tmp/timewiki_backup.log 2>&1
cat /tmp/timewiki_backup.log >> /var/log/crond/timewiki_backup.log
rm /tmp/timewiki_backup.log
