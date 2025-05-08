#!/bin/bash

if [[ "$1" == "stop" ]]; then
    # Stop Prometheus
    echo "Stopping Prometheus..."
    sudo pkill -f "prometheus"

    # Stop FlowLabel Exporter
    echo "Stopping FlowLabel Exporter..."
    sudo pkill -f "FlowLabel_Exporter.py"

    # Stop Grafana
    echo "Stopping Grafana..."
    sudo pkill -f "grafana-server"

    echo "All processes stopped!"
else
    # Stop Prometheus
    echo "Starting Prometheus on port 9000..."
    sudo prometheus --config.file=/etc/prometheus/prometheus.yml --web.listen-address=:9000 >> /var/log/prometheus.log 2>&1 &

    # Stop FlowLabel Exporter
    echo "Starting FlowLabel Exporter..."
    sudo python3 /home/hcy/scitags/FlowLabel_Exporter.py >> /var/log/FlowLabel_Exporter.log 2>&1 &

    # Stop Grafana
    echo "Starting Grafana..."
    cd /usr/local/grafana/bin
    ./grafana-server >> /var/log/grafana.log 2>&1 &
fi
