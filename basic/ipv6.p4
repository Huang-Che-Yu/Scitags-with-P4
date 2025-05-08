// SPDX-License-Identifier: Apache-2.0
/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV6 = 0x86DD;

/********************** H E A D E R S  **********************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;


header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv6_t {
    bit<4>    version;
    bit<8>    trafficClass;
    bit<20>   flowLabel;
    bit<16>   payloadLength;
    bit<8>    nextHeader;
    bit<8>    hopLimit;
    bit<128>  srcAddr;
    bit<128>  dstAddr;
}


struct metadata {
    bit<9> exp_id_reversed;
}

struct headers {
    ethernet_t   ethernet;
    ipv6_t       ipv6;
}

/********************** P A R S E R  ***********************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV6: parse_ipv6;
            default: accept;
        }
    }

    state parse_ipv6 {
        packet.extract(hdr.ipv6);
        transition accept;
    }

}

/***********   C H E C K S U M    V E R I F I C A T I O N   *************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************  I N G R E S S   P R O C E S S I N G   *******************/



control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    action drop() {
        mark_to_drop(standard_metadata);
    }

    action ipv6_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv6.hopLimit = hdr.ipv6.hopLimit - 1;
    }

    table ipv6_lpm {
        key = {
            hdr.ipv6.dstAddr: lpm;
        }
        actions = {
            ipv6_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = drop();
    }

    table dst_port_filter {
        key = {
            hdr.ipv6.dstAddr: lpm;
            standard_metadata.egress_spec: exact;
        }
        actions = {
            drop;
            NoAction;
        }
        size = 512;
        default_action = drop();
    }

    table flow_filter {
        key = {
            hdr.ipv6.flowLabel[7:2]: exact;
            meta.exp_id_reversed: exact;
        }
        actions = {
            NoAction;
        }
        size = 512;
        default_action = NoAction();
    }

    apply {
        if (hdr.ipv6.isValid()) {
            bit<9> experiment = hdr.ipv6.flowLabel[17:9];
            bit<9> exp_id_reversed = ((experiment & 0b000000001) << 8) |
                                     ((experiment & 0b000000010) << 6) |
                                     ((experiment & 0b000000100) << 4) |
                                     ((experiment & 0b000001000) << 2) |
                                     ((experiment & 0b000010000) << 0) |
                                     ((experiment & 0b000100000) >> 2) |
                                     ((experiment & 0b001000000) >> 4) |
                                     ((experiment & 0b010000000) >> 6) |
                                     ((experiment & 0b100000000) >> 8);
            
            meta.exp_id_reversed = exp_id_reversed;

            ipv6_lpm.apply();
            if(flow_filter.apply().hit){
                dst_port_filter.apply();
            }
        }
    }
}

/***************  E G R E S S   P R O C E S S I N G   *******************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
}

/************   C H E C K S U M    C O M P U T A T I O N   **************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {

    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv6);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
