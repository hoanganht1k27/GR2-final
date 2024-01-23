create database grafana;

grant all privileges on grafana.* to grafana@'%' identified by 'juniper@123';
grant all privileges on grafana.* to grafana@'localhost' identified by 'juniper@123';
grant all privileges on grafana.* to grafana@'127.0.0.1' identified by 'juniper@123';