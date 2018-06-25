export SSHPASS=time-pilot1
sshpass -e sftp -oBatchMode=no -b - pilot1@time.rit.edu << !
	cd incoming-file
	bye
!
