#sshpass -p "time-pilot1" ssh -o StrictHostKeyChecking=no pilot1@time.rit.edu

export SSHPASS=time-pilot1
sshpass -e sftp -oBatchMode=no -b - pilot1@time.rit.edu << !
	cd /data/cryo/current_data
	lcd ~/TIME_Software/Beta0.2/tempfiles/mce1
	put temp.*
	rm temp.*
	bye
!
