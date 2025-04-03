from p4runtime-shell import P4RuntimeShell

with P4RuntimeShell(device_id=1, grpc_addr="127.0.0.1:50051") as p4:
    activity_value = p4.register_read("activity_reg", 0)
    flowlabel_value = p4.register_read("flow_label_reg", 0)

    print(f"Activity[17:12]: {activity_value}")
    print(f"Full FlowLabel: {flowlabel_value}")
