## SVTECH-STACK
<p>
  
Ansible version
```
ansible [core 2.12.5]
  config file = /opt/SVTECH-installation-automation/ansible.cfg
  configured module search path = ['/Users/hoangtu/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location =  /usr/local/lib/python3.8/dist-packages/ansible
  ansible collection location = /opt/SVTECH-installation-automation/collections
  executable location = /usr/local/bin/ansible
  python version = 3.8.2 (default, Dec 21 2020, 15:06:04) [Clang 12.0.0 (clang-1200.0.32.29)]
  jinja version = 3.1.2
  libyaml = True
```

Required Collections
```
Collection        Version
----------------- -------
ansible.posix     1.3.0
community.crypto  1.9.5
community.general 3.8.0
community.mysql   3.1.3
```

Tree level directory structure:
```
.
├── LICENSE
├── README.md
├── ansible.cfg
├── collections
│   └── ansible_collections
├── database.yml
├── elk_beat.yml
├── elk_elastic.yml
├── environment.yml
├── host_info
├── inventories
│   ├── default
│   ├── production
│   └── staging
├── k8s.yml
├── nms.yml
├── nms_compose.yml
├── require_python
│   ├── host_list_module
│   └── remote_host_list_module
├── requirements.yml
├── roles
│   ├── ansible-beats
│   ├── ansible-elasticsearch
│   ├── ansible-pyenv
│   ├── database
│   ├── elk_beat
│   ├── elk_elastic
│   ├── environment
│   ├── k8s
│   ├── logstash
│   ├── nms
│   ├── nms_compose
│   ├── prometheus_exporter
│   ├── prometheus_server
│   └── svtech_elasticsearch
├── svtech_elasticsearch.yml
└── yaml_elasticsearch.yml
```

### How to use
- Git clone this repository to /opt
```
cd /opt/
git clone https://github.com/moophat/SVTECH-installation-automation.git
```
- Go to playbook directory:
```
cd /opt/SVTECH-installation-automation
```
- Install Ansible: https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html
- Install Collections:
```
ansible-galaxy collection install community.general
ansible-galaxy collection install ansible.posix
ansible-galaxy collection install community.crypto:1.9.5
ansible-galaxy collection install community.mysql:3.1.3
```
- Change IP address in inventory file at /opt/inventories/...
- And run playbook
</p>
