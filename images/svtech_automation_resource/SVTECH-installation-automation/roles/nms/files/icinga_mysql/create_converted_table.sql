CREATE TABLE IF NOT EXISTS icinga.icinga_servicechecks_converted (
    id BIGINT NOT NULL AUTO_INCREMENT,
    servicecheck_id BIGINT,
    instance_id BIGINT,
    service_object_id BIGINT,
    state SMALLINT,
    state_type SMALLINT,
    start_time BIGINT,
    command_object_id BIGINT,
    execution_time DOUBLE,
    PRIMARY KEY (id),
    key idx_ob_start (service_object_id, start_time)
) ENGINE = InnoDB COMMENT='Simplified Historical service checks';


CREATE TABLE IF NOT EXISTS icinga.icinga_hostchecks_converted(
    id BIGINT NOT NULL AUTO_INCREMENT,
    hostcheck_id BIGINT,
    instance_id BIGINT,
    host_object_id BIGINT,
    state SMALLINT,
    state_type SMALLINT,
    start_time BIGINT,
    command_object_id BIGINT,
    execution_time DOUBLE,
    PRIMARY KEY (id),
    key idx_ob_start (host_object_id, start_time)
) ENGINE = InnoDB COMMENT='Simplified Historical host checks';