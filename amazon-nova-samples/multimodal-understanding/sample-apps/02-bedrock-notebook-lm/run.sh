#!/bin/bash

# Check if an argument is provided
if [ $# -eq 0 ]; then
    echo "No arguments provided. Please provide an argument."
    exit 1
fi

# Assign the input argument to a variable
input=$1

# Execute commands based on the input argument
case $input in
    build)
        echo "Building image..."
        docker build -t opennotebooklm:latest .
        ;;
    run)
        echo "Running the app..."
	    docker run -d -p 7860:7860 -v ~/.aws:/root/.aws --name opennotebooklm opennotebooklm:latest 
        ;;
    stop)
        echo "Stopping the app..."
        docker stop opennotebooklm
        docker rm opennotebooklm
        # Command to check the status of a service
        # e.g., sudo systemctl status myservice
        ;;
    *)
        echo "Invalid argument. Please use build, run or stop."
        exit 1
        ;;
esac
