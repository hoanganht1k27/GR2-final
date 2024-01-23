import logging
import json
import os
import time

from ansible.module_utils.basic import *
from ansible.module_utils import NETWORK_FUNC
from ansible.module_utils import SNMPLibrary
from ansible.module_utils import BASE_FUNC
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

def main():
    module = AnsibleModule(
                           argument_spec=dict(networkAddress=dict(required=True, default=None),  # network address
                                               community=dict(required=False, default='public'),
                                               output_dir=dict(required=True),
                                               ping_interval = dict(required=False, default = 0.1, type = "float"),
                                               ping_count = dict(required=False, default = 3, type = "int"),
                                               collect_hostname = dict(required=False, default = True, type="bool"),
                                               log_prefix = dict(type = "str" , default = "scan_ip_subnet"),
                                               log_surfix = dict(type = "str" , default = ""),
                                               log_timestamp = dict(type = "str" , default = "%Y-%m-%d"),
                                               log_dir = dict(type = "str" , default = "./logs/"),
                                               log_level = dict(type = "str" , choices =  [ 'DEBUG' , 'INFO' , 'WARNING' , 'ERROR' , 'CRITICAL' ] ,default = "INFO"),
                                               list_full_oid = dict(required=False, type='list', default=None),
                               ),
                           supports_check_mode=True)
    args = module.params
    log_file    =    os.path.join(  args["log_dir"], 
                                    "{}_{}_{}.log".format(   args["log_prefix"],
                                                                time.strftime(args["log_timestamp"]),
                                                                args["log_surfix"])
                                )
    BASE_FUNC.LOGGER_INIT(log_level = args["log_level"],
                          log_file  = log_file,
                          print_log_init = True)
    logging.info("List of received arguments " + str(args))

    logging.info("Connecting to network: {0}:".format(args['networkAddress']))
    result = {"list_w_hostname":list(),"list_no_hostname":list(), "dict_snmp_values":dict()}
    try:
        start = time.time()
        aliveHost = NETWORK_FUNC.GET_ALIVE_HOST(args['networkAddress'],
                                                args['ping_interval'],
                                                args['ping_count'])
        end = time.time()
        logging.info("Time to ping all host: {}".format(end - start))
        logging.info("List of alive host:: {}".format(aliveHost))
        if aliveHost in [WARNING,CRITICAL]:
            result[0] = "Failed to obtain list of alive host"
        elif args['collect_hostname'] is True:
            logging.info ("Collecting all hostname using snmp community {}".format(args['community']))
            for eachHost in aliveHost:
                hostname = SNMPLibrary.CHECK_SNMP_HOSTNAME(eachHost, args['community'])
                if hostname == "":
                    logging.info("The host can be ping but doesn't have host name: {}, using IP address as hostname".format(eachHost))
                    result['list_no_hostname'].append({"IP": eachHost, "snmp_hostname": eachHost})
                else:
                    logging.info("Appending IP {} and hostname {}".format(eachHost,hostname))
                    result['list_w_hostname'].append({"IP": eachHost, "snmp_hostname": hostname})
                    if args['list_full_oid']:
                        # If user declare the argument "list_full_oid", return the result as the format:
                        # "hostname": {"full_oid": values}
                        # Get OID full - Start
                        snmp_list_values = SNMPLibrary.GET_SNMP_VALUES_FROM_LIST_OID(eachHost, args['community'], args['list_full_oid'])
                        result['dict_snmp_values'][eachHost] = snmp_list_values
                        # Get OID full - End
        else:
            logging.info("Returnning IP address only, not querying host name")
            for eachHost in aliveHost:
                logging.info("Appending IP {}".format(eachHost))
                result['list_no_hostname'].append({"IP": eachHost, "snmp_hostname": eachHost})
            
            end2 = time.time()
            logging.info("Time to get host name by using SNMP: {}".format(end2 - end))

    except Exception as err:
        msg = 'Uncaught exception - please report: {0}'.format(str(err))
        logging.exception(msg)
        module.fail_json(msg=msg)

    #Export data - Start
    if aliveHost not in [WARNING,CRITICAL]:
        with open(args['output_dir'], 'w') as output:
            for eachHost in result['list_w_hostname']:
                output.write('{}   ansible_host={}\n'.format(eachHost['snmp_hostname'], eachHost['IP']))
                logging.debug("Scan result: {} - {}".format(eachHost['snmp_hostname'], eachHost['IP']))
            for eachHost in result['list_no_hostname']:
                output.write('{}   ansible_host={}\n'.format(eachHost['snmp_hostname'], eachHost['IP']))
                logging.debug("Scan result: {} - {}".format(eachHost['snmp_hostname'], eachHost['IP']))
    #Export data - End
    data = dict()
    data["result"] = result
    data["logfile"] = log_file
    data['changed'] = True
    data['failed'] = False
    data["json_string"] = json.dumps(data, indent=4, sort_keys=True, ensure_ascii=True)
    module.exit_json(**data)


if __name__ == '__main__':
 main()
