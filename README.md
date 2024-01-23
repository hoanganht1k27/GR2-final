# Folders:
[images](/images) - Store all images definition (dockerfile, depedencies files, ...)

[lab-monitoring-helm](/lab-monitoring-helm) - Helm chart files for auto provisioning application in kubernetes

# Configuration instruction:
## Config vmware exporter:
Supply username, password, vcenter host in vmware-exporter configuration block in [values.yaml](/lab-monitoring-helm/values.yaml)

For example
```
vmware-exporter:
  vsphere:
    host: {{ vcenter_host }}
    user: {{ vcenter_user }}
    password: {{ vcenter_password }}
```

## Config proxmox exporter
Supply username, password in pve-exporter configuration block in [values.yaml](/lab-monitoring-helm/values.yaml)

For example
```
pve-exporter:
  user: {{ pve_user }}
  password: {{ pve_password }}
```

Supply list of proxmox host in prometheus.fileBaseConfig.pve configuration block in [values.yaml](/lab-monitoring-helm/values.yaml)

For example
```
prometheus:
  fileBaseConfig:
    pve: 
      - targets:
        - {{ proxmox_01 }}
        - {{ proxmox_02 }}
        labels:
          target_type: "pve"
```

## Config pnetlab exporter
Supply database, user, password in pnetlab-exporter configuration block in [values.yaml](/lab-monitoring-helm/values.yaml)

For example
```
pnetlab-exporter:
  replicaCount: 1

  databases:
    - host: {{ db_01 }}
      port: 3306
      user: prometheus
      password: pnetlab
    - host: {{ db_02 }}
      port: 3306
      user: prometheus
      password: pnetlab
```

## Config snmp exporter
Supply community for snmp exporter in snmp-exporter configuration block in [values.yaml](/lab-monitoring-helm/values.yaml)

For example
```
snmp-exporter:
  community: test
```

Supply list of physical server that turn on snmp agent using above community in prometheus.fileBaseConfig.snmp configuration block in [values.yaml](/lab-monitoring-helm/values.yaml)

For example
```
prometheus:
  fileBaseConfig:
    snmp: 
      - targets:
        - {{ server_01 }}
        - {{ server_02 }}
        - {{ server_03 }}
```



# Installation steps:
## Step 1: Install strimzi operator for deploying kafka
(For example using namespace default)

kubectl create -f 'https://strimzi.io/install/latest?namespace=default'

## Step 2: Run helm
### Command run for production deploy
helm install monitoring ./lab-monitoring-helm

### Command run for testing deploy 
helm install monitoring ./lab-monitoring-helm \
    --set mariadb-galera.replicaCount=1 \
    --set influxdb.influxdb.replicaCount=1 \
    --set proxy.replicaCount=1 \
    --set syncthing.replicaCount=3 \
    --set kafka_to_influxdb.replicaCount=1 \
    --set kafka.kafka.replicaCount=1 \
    --set kafka.zookeeper.replicaCount=1 \
    --set kafka.kafka.config.offsets_topic_replication_factor=1 \
    --set kafka.kafka.config.transaction_state_log_replication_factor=1 \
    --set kafka.kafka.config.transaction_state_log_min_isr=1 \
    --set kafka.kafka.config.default_replication_factor=1 \
    --set kafka.kafka.config.min_insync_replica=1 \
    --set kafka.kafka.config.log_retention_hours=4
