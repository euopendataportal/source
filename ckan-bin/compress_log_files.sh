#!/bin/sh
#This sript has to be executed with root
# compress all matching files older than one day
find /var/log/httpd -type f -name "*.log" -mtime +1 -exec gzip {} \;

# delete all files older then 7 days
find /var/log/httpd -type f -name "*" -mtime +7 -delete