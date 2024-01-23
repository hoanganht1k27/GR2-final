#!/usr/bin/python

import libvirt
import sys
import os
import argparse

# virDomainEventType is emitted during domain lifecycles (see libvirt.h)
VIR_DOMAIN_EVENT_MAPPING = {
    0: "VIR_DOMAIN_EVENT_DEFINED",
    1: "VIR_DOMAIN_EVENT_UNDEFINED",
    2: "VIR_DOMAIN_EVENT_STARTED",
    3: "VIR_DOMAIN_EVENT_SUSPENDED",
    4: "VIR_DOMAIN_EVENT_RESUMED",
    5: "VIR_DOMAIN_EVENT_STOPPED",
    6: "VIR_DOMAIN_EVENT_SHUTDOWN",
    7: "VIR_DOMAIN_EVENT_PMSUSPENDED",
}

# virDomainState
VIR_DOMAIN_STATE_MAPPING = {
    0: "VIR_DOMAIN_NOSTATE",
    1: "VIR_DOMAIN_RUNNING",
    2: "VIR_DOMAIN_BLOCKED",
    3: "VIR_DOMAIN_PAUSED",
    4: "VIR_DOMAIN_SHUTDOWN",
    5: "VIR_DOMAIN_SHUTOFF",
    6: "VIR_DOMAIN_CRASHED",
    7: "VIR_DOMAIN_PMSUSPENDED",
}


def conn_register_event_id_lifecycle(conn):
    conn.domainEventRegisterAny(
        None,
        libvirt.VIR_DOMAIN_EVENT_ID_LIFECYCLE,
        event_lifecycle_cb,
        conn)

def event_lifecycle_cb(conn, dom, event, detail, opaque):
    print("")
    print("=-" * 25)
    print("%s: event: %s (%s)" % (dom.name(), VIR_DOMAIN_EVENT_MAPPING.get(event, "?"), event))
    print("%s: state: %s (%s)" % (dom.name(), VIR_DOMAIN_STATE_MAPPING.get(dom.state()[0], "?"), dom.state()[0]))
    print("=-" * 25)
    action_for_event(event)

def action_for_event(event):
    if event == 0:
        if args.period:
            config_checkmem_period(args.period)


def config_checkmem_period(period_check):
    period = period_check
    command = """
    command=$(virsh list --all | awk '{print $2}' | xargs )
    period=%s
    for i in $command ; do
    if [[ $i != "Name" ]]; then
        virsh dommemstat "$i" --period $period --live --config;
        virsh dommemstat "$i" --period $period --current;
    fi
    done
    """ % str(period)
    os.system(command)
    print("Config dommemstat with period {}(s) DONE".format(period))

def Init_Arguments():
    """ Init Arguments """
    global args
    cmdline = argparse.ArgumentParser(description="Libvirt Event listener")
    cmdline.add_argument('--period' , '-p', action='store', help='Period memcheck update')
    args = cmdline.parse_args()
    return args

if __name__ == "__main__":
    Init_Arguments()
    if args.period:
        print("Init memcheck period !")
        config_checkmem_period(args.period)

    libvirt.virEventRegisterDefaultImpl()
    # setup connection
    conn = libvirt.open(('qemu:///system'))
    # conn=libvirt.open("xen:///")
    if conn == None:
        print('Failed to open connection to the hypervisor')
        sys.exit(1)

    # register events
    conn_register_event_id_lifecycle(conn)

    # event loop
    while True:
        libvirt.virEventRunDefaultImpl()

    sys.exit(0)
