import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
import BASE_FUNC
import NETWORK_FUNC
import PYEZ_BASE_FUNC
import time
import logging



OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

# List module type
def GET_JUNOS_PORTMODULE_DETAIL(dev,output_format,output_type,output_file):

    pic_data_type = "PICStatus"
    pic_tableview_file = "hardware_inventory.yml"
    pic_rpc_kwargs = None
    pic_output_format = "list_of_dict"
    pic_output_type = "object"
    try:

        PicStatusResult = PYEZ_BASE_FUNC.GET_JUNOS_DATA_TABLEVIEW_FORMATTED(dev,
                                                                            pic_data_type,
                                                                            pic_tableview_file,
                                                                            pic_rpc_kwargs,
                                                                            pic_output_format,
                                                                            pic_output_type)
        
        for item in PicStatusResult:
            rpc_kwargs = dict()
            rpc_kwargs['fpc-slot'] = item['fpc_slot']
            rpc_kwargs['pic-slot'] = item['pic_slot']

            PicStatusResult = PYEZ_BASE_FUNC.GET_JUNOS_DATA_TABLEVIEW_FORMATTED(dev,
                                                                                "PortModuleDetail",
                                                                                pic_tableview_file,
                                                                                rpc_kwargs,
                                                                                output_format,
                                                                                output_type,
                                                                                output_file,
                                                                                write_mode="a")
    except Exception as e:
        logging.error("Exception during collecting PortModule detail due to " + str(e))
        return CRITICAL
    return GET_JUNOS_PORTMODULE_DETAIL 
