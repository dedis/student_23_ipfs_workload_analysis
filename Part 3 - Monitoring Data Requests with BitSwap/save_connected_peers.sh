#!/bin/bash

while true; do
    # Get the current timestamp
    TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)_UTC

    # Create the directories if they don't exist
    mkdir -p connected_peers/docker_compose_monitor_01
    mkdir -p connected_peers/docker_compose_monitor_02

    # Run the curl commands
    curl http://127.0.0.1:8432/metric_plugin/v1/sample_peer_metadata >connected_peers/docker_compose_monitor_01/$TIMESTAMP.txt
    echo "Success: The file has been created with timestamp $TIMESTAMP for docker_compose_monitor_01"

    curl http://127.0.0.1:8433/metric_plugin/v1/sample_peer_metadata >connected_peers/docker_compose_monitor_02/$TIMESTAMP.txt
    echo "Success: The file has been created with timestamp $TIMESTAMP for docker_compose_monitor_02"

    # Sleep for 60 minutes
    sleep 3600
done
