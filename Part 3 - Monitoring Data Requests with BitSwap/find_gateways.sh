#!/bin/bash

# Directory to store the gateways
GATEWAYS_DIR=gateways

# Create the directory if it doesn't exist
mkdir -p $GATEWAYS_DIR

while true; do
    # Get current timestamp
    TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)

    # Run ipfs-gateway-finder for each monitor
    for MONITOR in 01 02; do
        ipfs-gateway-finder --monitor-name docker_compose_monitor_$MONITOR >$GATEWAYS_DIR/gateways-$MONITOR-$TIMESTAMP.json

        # Print success message
        echo "$(date +%Y-%m-%d_%H-%M-%S): Successfully ran ipfs-gateway-finder for monitor $MONITOR and stored in gateways-$MONITOR-$TIMESTAMP.json"
    done

    # Sleep for 12 hours
    sleep 12h
done
