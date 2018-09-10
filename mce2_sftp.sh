sftp -oBatchMode=no -b time@time-mce-0.caltech.edu << EOF
	cd /data/cryo/current_data
	lcd ~/TIME_Software/Beta0.2/tempfiles/mce1
	put temp.*
	rm temp.*
	bye
EOF
