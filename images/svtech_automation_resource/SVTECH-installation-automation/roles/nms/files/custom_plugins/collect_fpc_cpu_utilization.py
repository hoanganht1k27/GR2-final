#!/usr/bin/python

import os
import time
import logging
import argparse
import ast
import sys
import BASE_FUNC


from jnpr.junos import Device
import jtextfsm

from pprint import pprint

def ICINGA2_MODE_ARGS_INIT(parser):
    icinga2_options = parser.add_argument_group( #actually not neccessary, for Gooey GUI only
        "Icinga2 output options", 
        "Customize the options to output collected data to Icinga2, DO NOT USE THIS MODE IN GUI",
    )
    icinga2_options.add_argument('-f',
                                  '-fpc_name', 
                                   type=str,
                                   dest = "fpc_name",
                                   required = True,
                                   help='       Name of the fpc to be collected')
    icinga2_options.add_argument('-t',
                                  '-template_file', 
                                   type=str,
                                   dest = "template_file",
                                   required = True,
                                   help='       Name of the textfsm template file to parse fpc output')

    icinga2_options.add_argument('-pdf', 
                                   '--perf_data_field', 
                                   #action='append', #use this because Icinga2 can repeat keyword argument, which is slightly more clear than nargs and "field1 field2 field3"
                                   #type=str,
                                   type=ast.literal_eval,
                                   dest = "perf_data_field",
                                   required = True,
                                   help='        List of specific data field to be printed into Icinga2 performance data output,, repeat key to add more item to the list')

def PYEZ_CONNECTION_ARGS_INIT(parser):
    # ===================================================CONNECTION PARAMETER=======================================================
    
    connection_options = parser.add_argument_group( #actually not neccessary, for Gooey GUI only
         "PyEZ connection Options", 
         "Customize the options to connect to Junos device"
    )
    connection_options.add_argument( '-ha', 
                         '--host_address', 
                         dest = "host_address",
                         type=str,
                         default = None,
                         help='One single address of device to connect, not required if host_list or host_file is provided')

    connection_options.add_argument( '-p', 
                         '--port',
                         dest = "port",
                         type=str,
                         default="830",
                         help='Netconf port number to be user ')

    connection_options.add_argument('-u', 
                        '--username', 
                        dest = "username",
                        type=str,
                        help='username to authenticate')

    connection_options.add_argument('-pw', 
                        '--password', 
                        dest = "password",
                        type=str,
                        help='password to authenticate')

    connection_options.add_argument('-cm', 
                        '--console_connection_mode', 
                        dest = "console_connection_mode",
                        choices = [ 'telnet' , 'serial'] ,
                        type=str,
                        help='Mode of connection in case netconf over ssh is not available, choose between telnet/serial')

    connection_options.add_argument('-rt', 
                        '--rpc_timeout', 
                        dest = "rpc_timeout",
                        type=int,
                        default=30,
                        help='Timeout while wait for rpc response, default to 30sec to follow PyEZ predefined value')

def PARSE_ARGS_CLI():
    """Parse command-line args"""
    parent_parser_obj = argparse.ArgumentParser(description='\nRetrieve tableview information on a Junos device')

    PYEZ_CONNECTION_ARGS_INIT(parent_parser_obj)
    BASE_FUNC.INIT_LOGGING_ARGS(parent_parser_obj)
    ICINGA2_MODE_ARGS_INIT(parent_parser_obj)

    return parent_parser_obj.parse_args()

def main(args = PARSE_ARGS_CLI()):

    #=======================================Creating log and reviewing arguments===============================================#
    log_file    =    os.path.join( args.log_dir, 
                                   "{}_{}_{}.log".format(args.log_prefix,
                                                          time.strftime(args.log_timestamp),
                                                          args.log_surfix)
                                 )
    BASE_FUNC.LOGGER_INIT(args.log_level, log_file, print_log_init = False,shell_output= True)
    logging.info("List of received arguments: [ {} ] ".format(args))

    #=======================================CHECKING ADDRESS===============================================#
    if args.host_address == None:
        logging.warning("No IP addresses provided, exiting Icinga2 working mode")
        BASE_FUNC.PRINT_W_TIME("No IP addresses provided, exiting Icinga2 working mode")
        sys.exit(WARNING)

    #get data  after IP verification
    logging.info ("Fetching info from {}".format(args.host_address))

    if args.console_connection_mode:
      if args.console_connection_mode in [ 'telnet' , 'serial']:
          logging.warning("Creating connection to device in console mode using [{}] mode, this should only be use if netconf over ssh is not available".format(args.console_connection_mode))
          device = Device(host    =    args.host_address,
                          user    =    args.username,
                          passwd  =    args.password,
                          port    =    args.port,
                          mode    =    args.console_connection_mode)
      else:
          logging.error("Wrong console connection mode provided, must be telnet or serial (remove console_connection_mode option if using netconf over ssh) ")
          raise("Wrong console connection mode provided, must be telnet or serial (remove console_connection_mode option if using netconf over ssh) ")
    else: 
          device = Device(host    =    args.host_address,
                          user    =    args.username,
                          passwd  =    args.password,
                          port    =    args.port)

    try:
        command="start shell command \"cprod -A {} -c 'show thread'\"".format(args.fpc_name)
        device.open(auto_probe=5)
        raw_result=device.cli(command)
        logging.debug("Raw output from {} - {}  is \n{}".format(args.host_address, args.fpc_name, raw_result))
    except Exception as e:
        logging.error ("Error getting cli output from host {} , fpc {} due to : [ {} ]".format(args.host_address, args.fpc_name,e) )
        BASE_FUNC.PRINT_W_TIME("Error getting cli output from host {} , fpc {} due to : [ {} ]".format(args.host_address, args.fpc_name,e) )
        BASE_FUNC.PRINT_W_TIME ("See log file {}".format(log_file))
        sys.exit(CRITICAL)

    logging.info ("Formating output from fpc {} using template file {}".format(args.fpc_name, args.template_file))
    try:
        with open(args.template_file, 'r') as template:
            result_table_schema = jtextfsm.TextFSM(template)
            fsm_results = result_table_schema.ParseText(raw_result)
            collection_of_results = [dict(zip(result_table_schema.header, element)) for element in fsm_results]
        
            logging.debug("Parsed output from  {} - {} is \n{}".format(args.host_address, args.fpc_name, collection_of_results)) 
    except Exception as e:
        logging.error ("Error parsing cli output from host {} , fpc {} due to : [ {} ]".format(args.host_address, args.fpc_name,e) )
        BASE_FUNC.PRINT_W_TIME("Error parsing cli output from host {} , fpc {} due to : [ {} ]".format(args.host_address, args.fpc_name,e) )
        BASE_FUNC.PRINT_W_TIME ("See log file {}".format(log_file))
        sys.exit(CRITICAL)

    try:
        icinga2_result_string = "Data collected ok so far, check influxdb | "
        if args.perf_data_field == None:
            logging.warning("No data field specified, nothing will be printed to Icinga2 performance data output")
            icinga2_result_string += " "  # append nothing
        else:
            for result_item in collection_of_results: #traverse list of process
                for fieldname in result_item: #traverse  each field in each process
                    if fieldname in args.perf_data_field:
                        if result_item['Name']!= None: result_item['Name']= str(result_item['Name']).replace(" ","_") #influxdb do not like space
                        if result_item[fieldname]!= None: result_item[fieldname] = str(result_item[fieldname]).replace(" ","_")
                        if fieldname!= None: fieldname = str(fieldname).replace(" ","_")
                        icinga2_result_string += "'{}[{}]'={};;;; ".format(result_item['Name'], fieldname , result_item[fieldname])
                        #icinga2_result_string += "'{}'={};;;; ".format(fieldname , result_item[fieldname])
        print(icinga2_result_string)
    except Exception as e:
        logging.error ("Error printing perfdata output to Icinga2  due to: [ {} ]".format(e) )
        BASE_FUNC.PRINT_W_TIME ("Error printing perfdata output to Icinga2  due to: [ {} ]".format(e) )
        BASE_FUNC.PRINT_W_TIME ("See log file {}".format(log_file))
        sys.exit(UNKNOWN)

if __name__ == "__main__":
    main()
