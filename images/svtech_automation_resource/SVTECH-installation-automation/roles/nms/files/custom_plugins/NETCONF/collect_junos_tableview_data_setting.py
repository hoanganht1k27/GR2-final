

output_prefix = "hardware"
output_surfix = ""
output_timestamp = "%d"
output_dir = "."

log_prefix = "hardware_inventory"
log_surfix = ""
log_timestamp = "_%d_%m"
log_dir = "."
log_level = "INFO"



#host_address = "123.29.8.1" # provide a single host here
host_list = [ "123.29.35.6" ] # ,"10.96.10.101", "10.96.10.102"  ] # provide a list of host here
#host_file = "list_device.yml" # provide the name that contain a list of host here
#note : all device from the above 3 option will be queried

port = "23"
console_connection_mode = "telnet"
username = "svtech-tool"
password = "SvtHanoi!"
# username= "juniper"
# password = "juniper@123"


tableview_file ="../Junos_tableview/hardware_state.yml"
# data_type = "FPC_Enviroment"
data_type = "FPC_Specific_Exhaust_A_Enviroment"
rpc_kwargs = {"fpc-slot": "0"}
#data_field= ["OpticTX", "OpticRX"]
#perf_data_field= [ "OpticTX"]


output_format ="csv" 
output_type ="file"
