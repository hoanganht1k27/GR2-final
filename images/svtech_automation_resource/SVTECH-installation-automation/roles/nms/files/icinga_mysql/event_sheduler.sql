SET GLOBAL event_scheduler="ON";

delimiter |
CREATE EVENT Convert_icinga_servicechecks
ON SCHEDULE EVERY 5 MINUTE
STARTS now()
ON COMPLETION NOT PRESERVE ENABLE
DO
  BEGIN
    INSERT INTO icinga.icinga_servicechecks_converted (servicecheck_id, instance_id, service_object_id, state, state_type, start_time, command_object_id, execution_time)
    SELECT servicecheck_id, instance_id, service_object_id, state, state_type, UNIX_TIMESTAMP(start_time), command_object_id, execution_time FROM icinga.icinga_servicechecks;
    DELETE FROM icinga.icinga_servicechecks;
  END |
delimiter ;


delimiter |
CREATE EVENT Convert_icinga_hostchecks
ON SCHEDULE EVERY 5 MINUTE
STARTS now()
ON COMPLETION NOT PRESERVE ENABLE
DO
  BEGIN
    INSERT INTO icinga.icinga_hostchecks_converted (hostcheck_id, instance_id, host_object_id, state, state_type, start_time, command_object_id, execution_time)
    SELECT hostcheck_id, instance_id, host_object_id, state, state_type, UNIX_TIMESTAMP(start_time), command_object_id, execution_time FROM icinga.icinga_hostchecks;
    DELETE FROM icinga.icinga_hostchecks;
  END |
delimiter ;