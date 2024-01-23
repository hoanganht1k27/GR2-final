#!/usr/bin/python
 
import subprocess
import os
import argparse
import re
import sys
import time
import logging
import BASE_FUNC

 
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3
 
 
def PARSE_ARGS ( args = None , namespace = None ) :
    """Parse command-line args"""
    mainparser = argparse.ArgumentParser ( description = '\nCheck Device config and upload if neccessary  ' )

    # ===================================================Logging Parameter======================================================
    BASE_FUNC.INIT_LOGGING_ARGS(mainparser)

    # =======WRAPPER PARAMETER==========================
 
    mainparser.add_argument       ('--check_snmp_path' ,
                                  dest = 'check_snmp_path' ,
                                  type = str ,
                                  default = '/usr/share/icinga2/plugins/libexec/' ,
                                  help = '\tdirectory to check_snmp stupid file' )
 
    mainparser.add_argument       ('--oid_text_index' ,
                                  dest = 'oid_text_index' ,
                                  type = str ,
                                  help = '\toid index in text form',
                                  required = True)
 
    mainparser.add_argument       ('--oid_text_index2' ,
                                  dest = 'oid_text_index2' ,
                                  type = str ,
                                  help = '\toid index in text form2',)
 
    mainparser.add_argument       ('--oid_prefix' ,
                                  dest = 'oid_prefix' ,
                                  type = str ,
                                  help = '\toid prefix in original decimal  form',
                                  required = True)
 
    mainparser.add_argument       ('--oid_surfix' ,
                                  dest = 'oid_surfix' ,
                                  type = str ,
                                  help = '\toid surfix in original decimal  form')

    # =======ORIGINAL CHECK_SNMP PARAMETER==========================
    mainparser.add_argument        ('--hostname' ,
                                  dest = 'hostname' ,
                                  type = str ,
                                  help = '\thostname or IP',
                                  required = True)
 
    mainparser.add_argument        ('--community' ,
                                  dest = 'community' ,
                                  type = str ,
                                  help = '\tSNMP com',
                                  required = True)
 
    mainparser.add_argument       ('--timeout' ,
                                  dest = 'timeout' ,
                                  type = int ,
                                  default = 10 ,
                                  help = '\ttimeout in seconds' )
 
    mainparser.add_argument       ('--units' ,
                                  dest = 'units' ,
                                  type = str ,
                                  default = 'Unknow_unit' ,
                                  help = '\tvalue unit' )
 
    mainparser.add_argument       ('--warning' ,
                                  dest = 'warning' ,
                                  type = str ,
                                  help = '\twarning threshold' )

    mainparser.add_argument       ('--critical' ,
                                  dest = 'critical' ,
                                  type = str ,
                                  help = '\tcritical threshold' )

    mainparser.add_argument       ('--label' ,
                                  dest = 'label' ,
                                  type = str ,
                                  help = '\tPrefix label for output from plugin (without this icinga2 influxdbwriter will write incorrect tag metric into influxdb)' )
    return mainparser.parse_args()

 

 
def TEXT_TO_SNMP_OID(text_value):
    """REPLACE TEXT CHARACTER WITH ASCII CHARACTER, ADDING "." IN BETWEEN TO CREATE SNMP OID"""
    try:
        if text_value != None:
            logging.debug("Translating text value <<" + text_value + ">> to snmp oid")
            oid_decimal_index = ""
            for char in text_value:
                oid_decimal_index += "." + str(ord(char))
            return oid_decimal_index
        else: 
            print "No text value is provided, oid will not be generate " 
            return WARNING 
    except Exception as local_e:
        print "Error Converting text value " + text_value + "to ASCII char due to: " + str(local_e)
        return CRITICAL
# Main
def main(args = PARSE_ARGS(), current_time = BASE_FUNC.TIME_INIT()):
    args.log_dir = args.check_snmp_path
    args.log_prefix = "check_snmp_" + args.log_prefix
    #=======================================Creating log directory===============================================#
    log_file    =    os.path.join( args.log_dir, args.log_prefix + time.strftime(args.log_timestamp) + args.log_surfix + '.log' )
    BASE_FUNC.LOGGER_INIT(args.log_level, log_file, print_log_init = False, shell_output = False)

    #=======================================Double check argument===============================================#
    for arg in vars(args):
        logging.debug( str(arg) + " " + str(getattr(args, arg)) )

    #=======================================Constructing OID - this should be converted to a function=================#
    oid_decimal_index = TEXT_TO_SNMP_OID(args.oid_text_index) 
    if oid_decimal_index not in [WARNING, CRITICAL]:
        oid_full = str(args.oid_prefix) + str( oid_decimal_index )
        logging.info ("Converted text index 1" + str(args.oid_text_index) + " to SNMP OID +" + oid_decimal_index)
    else:
        BASE_FUNC.PRINT_W_TIME("Exiting due to problem with oid_text_index :" + args.oid_text_index)
        sys.exit(oid_decimal_index)

    if args.oid_text_index2:
        oid_decimal_index = TEXT_TO_SNMP_OID(args.oid_text_index) 
        if oid_decimal_index not in [WARNING, CRITICAL]:
            oid_full = oid_full + str( oid_decimal_index ) 
            logging.info ("Converted text index 2" + str(args.oid_text_index2) + " to SNMP OID +" + oid_decimal_index)
        else:
            BASE_FUNC.PRINT_W_TIME("Exiting due to problem with oid_text_index2 :" + args.oid_text_index2)
            sys.exit(oid_decimal_index)

    if args.oid_surfix:
        if args.oid_surfix.startswith("."):
            oid_full+= str(args.oid_surfix)       #append surfix if already start with . delimiter
        else:
            oid_full+= "." + str(args.oid_surfix)       #append . if surfix do no have it 
        logging.info ("Appending surfix " + str(args.oid_surfix) + " to SNMP OID format")

    logging.debug("Constructed OID <<<<<" + str(oid_full) + ">>>>>")
     
     
    #=============================================Passing parameter to external check_snmp================
    check_snmp_command = os.path.join(args.check_snmp_path,"check_snmp ")
     
    for arg in vars(args): 
            if arg not in [ "check_snmp_path" , "oid_text_index", "oid_text_index2", "oid_prefix", "oid_surfix"] and not  re.match ('^.*log*.*$', arg ): #exclude wrapper script argument, pass all other argument to the original check_snmp script
                    check_snmp_command += " --" + arg + " " + str(getattr(args, arg))
     
    check_snmp_command += " --oid" + " " + oid_full
    logging.debug("Constructed OID <<<<<" + str(check_snmp_command) + ">>>>>")
     

    #=============================================Calling external check_snmp=============================
    try:
        logging.debug("Calling check_snmp main file ")
        check_result = subprocess.check_output( str(check_snmp_command), shell=True, cwd =  args.check_snmp_path )
    except Exception as e:
        check_result = e.output
        logging.debug("Calling check_snmp subprocess return NON-ZERO (NOT-OK STATUS)  <<<<<" + str(e) + ">>>>>") #do not change to error or warning to avoid print to icinga
    
    logging.debug("Check result before trimming is " + str(check_result))
    result_trimmer = { "SNMP\s\w+ - \w+" : " "}
    check_result = BASE_FUNC.MULTI_REGEX_REPLACE(result_trimmer,str(check_result))
    

    exit_code = UNKNOWN
    
    if re.match ( '.*Unknown Object Identifier*.*' , check_result ):
            print "OID DO NOT EXIST?? (CASE 1)"
            exit_code = UNKNOWN
    
    elif re.match ( '.*\n.*noSuchName*.*' , check_result ):
            print "OID DO NOT EXIST?? (CASE 2)"
            exit_code = UNKNOWN
    
    elif re.match ( '.*\n.*No Such*.*' , check_result ):
            print "OID DO NOT EXIST?? (CASE 3)"
            exit_code = UNKNOWN
    
    elif re.match ( '^.*WARNING.*$' , check_result ):
            exit_code = WARNING
    
    elif re.match ( '^[I,i]nf.*$' , check_result ):
            exit_code = CRITICAL
    
    elif re.match ( '^.*CRITICAL.*$' , check_result ):
            exit_code = CRITICAL
    
    elif re.match ( '^.*command error.*$' , check_result ):
            exit_code = CRITICAL
    
    elif re.match ( '^.*OK.*$' , check_result ):
            exit_code = OK
    
    elif re.match ( '.*\d*.*' , check_result ):
            exit_code = OK
    
    else:
            exit_code = UNKNOWN
    
    print check_result
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
