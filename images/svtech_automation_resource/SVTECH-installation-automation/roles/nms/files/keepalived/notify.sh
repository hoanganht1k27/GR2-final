#!/bin/bash

TYPE=$1
NAME=$2
STATE=$3

case $STATE in
        "MASTER") icinga2 feature enable notification
                  icinga2 feature enable ido-mysql
                  service rundeckd restart
                  service icinga2 reload
                  service icinga2-report restart
                  service grafana-server restart
                  service httpd restart
#		  sed -i 's/^systemctl/#systemctl/g' /etc/icinga2/conf.d/managed/.git/hooks/post-commit
                  sh /etc/keepalived/master.sh
                  exit 0
                  ;;
        "BACKUP") icinga2 feature disable notification
                  icinga2 feature enable ido-mysql
                  service rundeckd stop
                  service icinga2 reload
                  service icinga2-report restart
                  service grafana-server restart
                  service httpd restart
#		  sed -i 's/#//g' /etc/icinga2/conf.d/managed/.git/hooks/post-commit
		  sleep 30
                  sh /etc/keepalived/slave.sh
                  exit 0
                  ;;
        "FAULT")  icinga2 feature disable notification
                  icinga2 feature enable ido-mysql
                  service rundeckd stop
                  service icinga2 reload
                  service icinga2-report restart
                  service grafana-server restart
                  service httpd restart
#		  sed -i 's/#//g' /etc/icinga2/conf.d/managed/.git/hooks/post-commit
		  sleep 30
                  sh /etc/keepalived/slave.sh
                  exit 0
                  ;;
        *)        echo "unknown state"
                  exit 1
                  ;;
esac
