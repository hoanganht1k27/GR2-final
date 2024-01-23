set -e
mysql -uroot -pjuniper@123 -e "STOP SLAVE IO_THREAD;"
mysql -uroot -pjuniper@123 -e "stop slave;"
mysql -uroot -pjuniper@123 -e "reset master;"
