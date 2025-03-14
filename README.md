# Scitags-with-P4

## 20250314

- install [flowd](https://github.com/scitags/flowd) and set flowd.cfg
    ```
    PLUGIN='netstat'
    BACKEND='prometheus,ebpf'
    NETSTAT_EXPERIMENT=16
    NETSTAT_ACTIVITY=14
    NETWORK_INTERFACE='eth0'
    FLOW_MAP_API='http://localhost:5000/FlowMapAPI.json'
    PROMETHRUS_SRV_PORT=9000
    ```
    flow map api must connect to http/https but host in mininet can not connect to internet. I used the Flask package to write `app.py` and hosted `FlowMapAPI.json` on h1's localhost.

- `eBPF` is a tool for packet marking. During initialization, it sets up the network interface to be monitored. However, the host's interface is netem, which causes the program to fail.

    Therefore, in `ebpf.py`'s `ebpf_init()`, replace:
    ```
    ipr.tc("del", "sfq", idxdict[key], "10:")
    ```
    with
    ```
    ipr.tc("del", "netem", idxdict[key], "10:")
    ```

- Change the IPV6 address from `fd00::00/112` to `bbff::00/112` since netstat netstat does not accept private IPs.

- After starting app.py and flowd on h1, establish a TCP connection with h2 using `iperf3`. By observing h1's eth0 with Wireshark, we can see that the Flow Label field in the outgoing IPv6 packets is correctly marked.

## 20250304

- Add ipv6.p4. It's almost the same as basic.p4

- Hosts can ping each other with **IPV6** through fix NDP settings


## 20250303
- Building topology 

- Hosts can ping each other with **IPV4**

- Setting IPV6 route & NDP on Hosts
