#!/bin/bash

PID_FILE="tmps/vllm.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    echo "Stopping vLLM with PID $PID"
    kill $PID
    rm "$PID_FILE"
else
    echo "PID file not found. Is vLLM running?"
fi