#!/usr/bin/env python

import os
import time
import logging
import argparse
import ast

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#import module_utils.BASE_FUNC as BASE_FUNC
#import module_utils.NETWORK_FUNC as NETWORK_FUNC
#import module_utils.PYEZ_BASE_FUNC as PYEZ_BASE_FUNC
from module_utils import Hardware
from module_utils import BASE_FUNC
from module_utils import PYEZ_BASE_FUNC
from module_utils import NETWORK_FUNC
#from TableviewExtension.Hardware import GET_JUNOS_PORTMODULE_DETAIL


from jnpr.junos import Device
from lxml import etree 

from pprint import pprint


OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3


current_os = sys.platform
if "win" in current_os:
    from gooey import Gooey, GooeyParser
    #only activate when using binary
    BASE_FUNC.SET_UNBUFFERED_STDOUT()
    print ( 'Created Unbuffered stdout for Gooey binary')

def ICINGA2_MODE_ARGS_INIT(parser):
    icinga2_options = parser.add_argument_group( #actually not neccessary, for Gooey GUI only
        "Icinga2 output options", 
        "Customize the options to output collected data to Icinga2, DO NOT USE THIS MODE IN GUI",
    )
    icinga2_options.add_argument('-df', 
                                   '--data_field', 
                                   #action='append', #use this because Icinga2 can repeat keyword argument, which is slightly more clear than nargs and "field1 field2 field3"
                                   #type=str,
                                   type=ast.literal_eval,
                                   dest = "data_field", 
                                   required = True,
                                   help='        List of specific data field to be printed into Icinga2 output, repeat key to add more item to the list')

    icinga2_options.add_argument('-pdf', 
                                   '--perf_data_field', 
                                   #action='append', #use this because Icinga2 can repeat keyword argument, which is slightly more clear than nargs and "field1 field2 field3"
                                   #type=str,
                                   type=ast.literal_eval,
                                   dest = "perf_data_field",
                                   required = True,
                                   help='        List of specific data field to be printed into Icinga2 performance data output,, repeat key to add more item to the list')

    icinga2_options.add_argument('-pk', 
                                   '--print_item_key', 
                                   type=BASE_FUNC.PARSE_BOOLEAN_ARGS,
                                   dest = "print_item_key",
                                   default = False,
                                   help='        Whether to print the value of the key(index) of each tableview item to Icinga stdout')
    icinga2_options.add_argument('--perf_data_item_key', 
                                   type=BASE_FUNC.PARSE_BOOLEAN_ARGS,
                                   dest = "perf_data_item_key",
                                   default = False,
                                   help='        Whether to output the value of the key(index) of each tableview item to Icinga performance data output')

def STANDALONE_MODE_ARGS_INIT(parser):
    standalone_options = parser.add_argument_group( #actually not neccessary, for Gooey GUI only
        "standalone mode  options", 
        "Customize the options to run in standalone mode",
    )


    standalone_options.add_argument( '-hl', 
                                       '--host_list', 
                                       dest = "host_list",
                                       #action='append',
                                       #nargs='+',
                                       type=ast.literal_eval,
                                       default = None,
                                       help='        A list of addresses of device to connect')

    if "win" in sys.platform.lower():
        standalone_options.add_argument( '-hf', 
                                           '--host_file', 
                                           dest = "host_file",
                                           type=str,
                                           default = None,
                                           widget = 'FileChooser',
                                           help='        yml file contain list of device to connect')
        
        # Custom setting file to be loaded (overwrite cli choice)
        standalone_options.add_argument( "--custom_setting_file" ,
                                           dest = "custom_setting_file" ,
                                           type = str ,
                                           default = None,
                                           widget = 'FileChooser',
                                           help = "Custom setting file to be exported " )
    else:
        standalone_options.add_argument( '-hf', 
                                           '--host_file', 
                                           dest = "host_file",
                                           type=str,
                                           default = None,
                                           help='        yml file contain list of device to connect')
        
        # Custom setting file to be loaded (overwrite cli choice)
        standalone_options.add_argument( "--custom_setting_file" ,
                                           dest = "custom_setting_file" ,
                                           type = str ,
                                           default = None,
                                           help = "Custom setting file to be exported " )


#Inside Gooey decorator, the function wrapper do not pass argument to the decorated function. use a global list of initiator functions as a workaround  
common_argument_init_functions = [ PYEZ_BASE_FUNC.TABLEVIEW_ARGS_INIT,
                                   PYEZ_BASE_FUNC.PYEZ_CONNECTION_ARGS_INIT,
                                   BASE_FUNC.INIT_OUTPUT_FILE_ARGS,
                                   BASE_FUNC.INIT_LOGGING_ARGS]

if "win" in current_os:
    @Gooey( program_name="Retrieve tableview information on a Junos device",
            navigation='TABBED',
            required_cols=1,
            optional_cols=3,
            dump_build_config=False,
            default_size=(900, 600))
    def PARSE_ARGS_JUNOS_TABLEVIEW_GOOEY():
        """Parse command-line args using Gooey UI utilitizes"""


        #main argument parsing steps
        global common_argument_init_functions
        parent_parser_obj = GooeyParser(description='\nRetrieve tableview information on a Junos device')
        #put arguments after this line to be inherited by all subparser, useful if Gooey is not involved.
    
        # ===================================================CREATE SUB PARSER TO DETERMINE WORKING MODE=====================================
        parser_obj = GooeyParser(description='\nRetrieve any defined information on a Junos device')
        #Note: parser_obj and parent_parser_obj must be 2 different ArgumentParser otherwise inheritance will be looped
        subparser_object = parser_obj.add_subparsers(help='Working mode', dest = "working_mode")
    
        # ===================================================STANDALONE MODE SPECIFIC PARAMETER===============================================
        # use parent_parser_obj to inherit previous arguments, add_help = False to re-use parent's help argv, avoid conflict
        standalone_subparser = subparser_object.add_parser("StandAlone",
                                                           parents = [parent_parser_obj], #do NOT put parser_obj here, loop will happen
                                                           add_help=False)
        #inherit tablview   related  arguments
        #TABLEVIEW_ARGS_INIT(standalone_subparser) 
        common_argument_init_functions[0](standalone_subparser)
        
        STANDALONE_MODE_ARGS_INIT(standalone_subparser)
    
        #inherit pyez connection related  argument from PYEZ_BASE_FUNC
        #PYEZ_BASE_FUNC.PYEZ_MODULE_COMMON_ARGS(standalone_subparser) 
        common_argument_init_functions[1](standalone_subparser)
        #inherit output file argument from BASE_FUNC
        #BASE_FUNC.INIT_OUTPUT_FILE_ARGS(standalone_subparser) 
        common_argument_init_functions[2](standalone_subparser)
        #inherit logging argument from BASE_FUNC
        #BASE_FUNC.INIT_LOGGING_ARGS(standalone_subparser) 
        common_argument_init_functions[3](standalone_subparser)
    
    
        # ===================================================ICINGA2 SPECIFIC PARAMETER======================================================
        # use parent to inherit previous arguments, add_help = False to re-use parent's help argv, avoid conflict
        icinga2_subparser = subparser_object.add_parser("Icinga2",
                                                        parents = [parent_parser_obj], 
                                                        add_help=False)
        #inherit tablview   related  arguments
        #TABLEVIEW_ARGS_INIT(icinga2_subparser) 
        common_argument_init_functions[0](icinga2_subparser)
    
        ICINGA2_MODE_ARGS_INIT(icinga2_subparser)
    
        #inherit pyez connection related  argument from PYEZ_BASE_FUNC
        #PYEZ_BASE_FUNC.PYEZ_MODULE_COMMON_ARGS(icinga2_subparser) 
        common_argument_init_functions[1](icinga2_subparser)
        #inherit output file argument from BASE_FUNC
        #BASE_FUNC.INIT_OUTPUT_FILE_ARGS(icinga2_subparser) 
        common_argument_init_functions[2](icinga2_subparser)
        #inherit logging argument from BASE_FUNC
        #BASE_FUNC.INIT_LOGGING_ARGS(icinga2_subparser) 
        common_argument_init_functions[3](icinga2_subparser)
    
        return parser_obj.parse_args()
        #return parent_parser_obj


def PARSE_ARGS_JUNOS_TABLEVIEW_CLI():
    """Parse command-line args"""
    global common_argument_init_functions
    parent_parser_obj = argparse.ArgumentParser(description='\nRetrieve tableview information on a Junos device')
    #put arguments here to be inherited by all subparser, useful if Gooey is not involved.
    for argument_init_func in common_argument_init_functions:
        argument_init_func(parent_parser_obj)
    # ===================================================CREATE SUB PARSER TO DETERMINE WORKING MODE=====================================
    parser_obj = argparse.ArgumentParser(description='\nRetrieve hardware information on a Junos device')
    #Note: parser_obj and parent_parser_obj must be 2 different ArgumentParser otherwise inheritance will be looped
    subparser_object = parser_obj.add_subparsers(help='Working mode', dest = "working_mode")

    # ===================================================STANDALONE MODE SPECIFIC PARAMETER===============================================
    # use parent_parser_obj to inherit previous arguments, add_help = False to re-use parent's help argv, avoid conflict
    standalone_subparser = subparser_object.add_parser("StandAlone",
                                                       parents = [parent_parser_obj], #do NOT put parser_obj here, loop will happen
                                                       add_help=False)
    STANDALONE_MODE_ARGS_INIT(standalone_subparser)

    # ===================================================ICINGA2 SPECIFIC PARAMETER======================================================
    # use parent to inherit previous arguments, add_help = False to re-use parent's help argv, avoid conflict
    icinga2_subparser = subparser_object.add_parser("Icinga2",
                                                    parents = [parent_parser_obj], 
                                                    add_help=False)
    ICINGA2_MODE_ARGS_INIT(icinga2_subparser)

    return parser_obj.parse_args()
    #return parent_parser_obj


if "win" in current_os:
    ARGUMENT_PARSER_FUNC = PARSE_ARGS_JUNOS_TABLEVIEW_GOOEY
elif "linux" in current_os:
    ARGUMENT_PARSER_FUNC = PARSE_ARGS_JUNOS_TABLEVIEW_CLI

# Main
def main(args = ARGUMENT_PARSER_FUNC(),current_time = BASE_FUNC.TIME_INIT()):
    #Determine platform
    if args.working_mode == "Icinga2":

        ##=======================================Import custom setting if available===============================================#
        #do not do this in Icinga2 working mode

        #=======================================Creating log and reviewing arguments===============================================#
        log_file    =    os.path.join( args.log_dir, 
                                       "{}_{}_{}.log".format(args.log_prefix,
                                                              time.strftime(args.log_timestamp),
                                                              args.log_surfix)
                                     )
        BASE_FUNC.LOGGER_INIT(args.log_level, log_file, print_log_init = False,shell_output= True)
        logging.info("List of received arguments: [ {} ] ".format(args))

        if args.host_address == None:
            logging.warning("No IP addresses provided, exiting Icinga2 working mode")
            BASE_FUNC.PRINT_W_TIME("No IP addresses provided, exiting Icinga2 working mode")
            sys.exit(WARNING)

        if NETWORK_FUNC.VERIFY_IPV4_ADDRESS( args.host_address ) != OK:
            logging.error("Exiting due to incorrect IP provided:[ {} ]".format(args.host_address))
            sys.exit(CRITICAL)
        
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

        if args.data_type == "PortModuleDetail" :
            result_raw = Hardware.GET_JUNOS_PORTMODULE_DETAIL( device, 
                                                  "raw",
                                                  args.output_type,
                                                  output_filefull)
        else:
            result_raw = PYEZ_BASE_FUNC.GET_PYEZ_TABLEVIEW_RAW( device,
                                                            args.data_type,
                                                            args.tableview_file,
                                                            args.rpc_kwargs)
        
        #keep this one , in case file write is needed
        #result_outputed = PYEZ_BASE_FUNC.FORMAT_PYEZ_TABLEVIEW(result_raw,
        #                                                      include_hostname=False,
        #                                                      output_format = args.output_format)
        #output_filename = "{}_{}_{}_{}.{}".format( args.output_prefix,
        #                                        args.data_type,
        #                                        args.output_timestamp,
        #                                        args.output_surfix,
        #                                        args.output_format)
        #output_filefull = os.path.join(args.output_dir, output_filename)

        result_printed = PYEZ_BASE_FUNC.FORMAT_PYEZ_TABLEVIEW(result_raw,
                                                              include_hostname=False,
                                                              output_format = "list_of_dict")

        if result_printed == WARNING or result_printed == CRITICAL:
            BASE_FUNC.PRINT_W_TIME ("Fetch data error, fetch result is : [ {} ]".format(result_printed) )
            BASE_FUNC.PRINT_W_TIME ("See log file {}".format(log_file))
            sys.exit(result_printed)

        icinga2_result_string  = ""
            #Constructing desired output data field
        try:
            if args.data_field == None:
                logging.warning("No data field specified, all field will be printed to Icinga2 output")
                icinga2_result_string = "{}".format(result_printed)
            else:
                for result_item in result_printed: #traverse PyEZ output item
                    for fieldname in result_item: #traverse  each field in each PyEZ output item
                        if fieldname in args.data_field:
                            if args.print_item_key == True:
                                icinga2_result_string += "{}[ {} ]= {}    ".format(result_item['tableview_key'], fieldname , result_item[fieldname])
                            else:
                                icinga2_result_string += "{}= {}    ".format(fieldname , result_item[fieldname])
        except Exception as e:
            logging.error ("Error printing output to Icinga2  due to: [ {} ]".format(e) )
            BASE_FUNC.PRINT_W_TIME ("Error printing output to Icinga2  due to: [ {} ]".format(e) )
            BASE_FUNC.PRINT_W_TIME ("See log file {}".format(log_file))
            sys.exit(UNKNOWN)

            #Constructing desired output performance metric field
        try:
            icinga2_result_string += " | " #after this will be performance data
            if args.perf_data_field == None:
                logging.warning("No data field specified, nothing will be printed to Icinga2 performance data output")
                icinga2_result_string += " "  # append nothing
            else:
                for result_item in result_printed: #traverse PyEZ output item
                    for fieldname in result_item: #traverse  each field in each PyEZ output item
                        if fieldname in args.perf_data_field:
                            if args.perf_data_item_key == True:
                                if result_item['tableview_key']!= None : result_item['tableview_key']= str(result_item['tableview_key']).replace(" ","_")
                                if fieldname!= None: fieldname = str(fieldname).replace(" ","_")
                                if result_item[fieldname]!= None: result_item[fieldname] = str(result_item[fieldname]).replace(" ","_")

                                icinga2_result_string += "'{}[{}]'={};;;; ".format(result_item['tableview_key'], fieldname , result_item[fieldname])
                            else:
                                icinga2_result_string += "'{}'={};;;; ".format(fieldname , result_item[fieldname])
        except Exception as e:
            logging.error ("Error printing perfdata output to Icinga2  due to: [ {} ]".format(e) )
            BASE_FUNC.PRINT_W_TIME ("Error printing perfdata output to Icinga2  due to: [ {} ]".format(e) )
            BASE_FUNC.PRINT_W_TIME ("See log file {}".format(log_file))
            sys.exit(UNKNOWN)
        
        #Printing then exit if nothing happend, adding threshold later
        if len(icinga2_result_string) != 0:
            logging.debug("Everything seemed ok, printed output [ {} ] to Icinga".format(icinga2_result_string) )
            print (icinga2_result_string)
            sys.exit(OK)
        else:
            logging.debug("Printed nothing to Icinga, let's check the data_type, tableview_file and data_field?" )
            sys.exit(WARNING)

    elif args.working_mode == "StandAlone":

        ##=======================================Import custom setting if available===============================================#
        BASE_FUNC.ARGS_SETTING_OVERRIDE(args.custom_setting_file,args)
        ##=======================================Gooey correction===============================================#
        #args.output_dir = args.output_dir.encode('unicode_escape').decode()
        #args.log_dir = args.log_dir.encode('unicode_escape').decode()
        #args.tableview_file = args.tableview_file.encode('unicode_escape').decode()
        #args.host_file = args.host_file.encode('unicode_escape').decode()
        #=======================================Creating log and reviewing arguments===============================================#
        log_file    =    os.path.join( args.log_dir, 
                                       "{}_{}_{}.log".format(args.log_prefix,
                                                              time.strftime(args.log_timestamp),
                                                              args.log_surfix)
                                     )
        BASE_FUNC.LOGGER_INIT(args.log_level, log_file, print_log_init = True,shell_output= True)
        logging.info("List of received arguments: [ {} ] ".format(args))

        list_device = []
        #Process host address if provided
        if args.host_address != None:
            list_device.append(args.host_address)

        #Process host list if provided
        if args.host_list != None:
            list_device.extend(args.host_list)

        #Process host file if provided
        if args.host_file != None:
            try:
                import yaml

                logging.debug("Opening host list file {}".format(args.host_file))
                with open(args.host_file,'r+') as  host_list_file:
                    list_device_yaml = yaml.load(host_list_file.read()) #loading hostlist from yaml file
            except Exception as e:
                logging.error ("Error opening hostlist file due to: [ {} ]".format(e) )
                sys.exit(CRITICAL)
            logging.debug ("Importing host list from yaml content: {}".format(list_device_yaml))
            for host_addr in list_device_yaml['Host']:
                list_device.append(host_addr)


        #eliminating duplicate
        fixed_list_device = list(set(list_device))
        logging.debug("Original device list generated is : {}".format(list_device))
        logging.info("Final device list is: {}".format(fixed_list_device))
        
        if len(fixed_list_device) == 0:
            logging.warning("No IP addresses provided, exiting StandAlone working mode")
            BASE_FUNC.PRINT_W_TIME("No IP addresses provided, exiting StandAlone working mode")
            sys.exit(WARNING)

        #Getting info one by one 
        for host_address in fixed_list_device:
            if NETWORK_FUNC.VERIFY_IPV4_ADDRESS( host_address ) != OK:
                logging.error("Skipping to next host due to incorrect IP provided: [ {} ]".format(host_address))
                continue

            if args.console_connection_mode:
                if args.console_connection_mode in [ 'telnet' , 'serial']:
                    logging.warning("Creating connection to device in console mode using [{}] mode, this should only be use if netconf over ssh is not available".format(args.console_connection_mode))
                    device = Device(host    =    host_address,
                                    user    =    args.username,
                                    passwd  =    args.password,
                                    port    =    args.port,
                                    mode    =    args.console_connection_mode)
                else:
                    logging.error("Wrong console connection mode provided, must be telnet or serial (remove console_connection_mode option if using netconf over ssh) ")
                    raise("Wrong console connection mode provided, must be telnet or serial (remove console_connection_mode option if using netconf over ssh) ")
            else: 
                  device = Device(host    =    host_address,
                                  user    =    args.username,
                                  passwd  =    args.password,
                                  port    =    args.port)

            if args.output_type == "object":

              if args.data_type == "PortModuleDetail":
                  result = Hardware.GET_JUNOS_PORTMODULE_DETAIL( device, 
                                                        args.output_format)
              else:
                  result = PYEZ_BASE_FUNC.GET_PYEZ_TABLEVIEW_FORMATTED( device,
                                                                        args.data_type,
                                                                        args.tableview_file,
                                                                        args.rpc_kwargs,
                                                                        True,
                                                                        args.output_format)
              pprint ("===============Result for [{}]=================\n{}".format(host_address,result))

            elif args.output_type == "file":
                output_filename = "{}_{}_{}_{}.{}".format( args.output_prefix,
                                                       args.data_type,
                                                       time.strftime(args.output_timestamp),
                                                       args.output_surfix,
                                                       args.output_format)
                output_filefull = os.path.join(args.output_dir, output_filename)
                if args.data_type == "PortModuleDetail" :
                    result_raw = Hardware.GET_JUNOS_PORTMODULE_DETAIL( device, 
                                                                      "raw",
                                                                      args.output_type,
                                                                      output_filefull)
                else:
                  raw_result = PYEZ_BASE_FUNC.GET_PYEZ_TABLEVIEW_RAW( device,
                                                                      args.data_type,
                                                                      args.tableview_file,
                                                                      args.rpc_kwargs)

                write_result = PYEZ_BASE_FUNC.WRITE_PYEZ_TABLEVIEW_FORMATTED( tableview_obj=raw_result,
                                                                              include_hostname=True,
                                                                              output_format = args.output_format,
                                                                              filename= output_filefull, 
                                                                              write_mode = "a")

                pprint ("Output file for [{}] is {}".format(host_address,output_filefull))
        #import code
        #code.interact(local=locals())
    else:
        logging.error("Invalid working mode specified {}".format(args.working_mode))
        sys.exit(CRITICAL)

if __name__ == "__main__":
    main()

