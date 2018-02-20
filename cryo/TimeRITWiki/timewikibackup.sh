
wget -P /data/TIME_Software/cryo/TimeRITWiki time.rit.edu \
    --http-user=time \
    --http-passwd=C2but!CO \
    --no-proxy \
    --recursive \
    --no-clobber \
    --page-requisites \
    --html-extension \
    --restrict-file-names=windows \
    --domains time.rit.edu \
    --no-parent \
    --wait=10 \
    --random-wait \
    --output-file=logfile \
    --continue \
    --directory-prefix=/data/TIME_Software/cryo/TimeRITWiki \
    --content-disposition \
    --user-agent="Mozilla" \
