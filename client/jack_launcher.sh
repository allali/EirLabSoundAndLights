#!/bin/bash

if [ "$1" = "stop" ]; then
    echo "Starting PulseAudio"
    systemctl --user start pulseaudio.socket && systemctl --user start pulseaudio.service
elif [ "$1" = "start" ]; then
    echo "Stopping PulseAudio"
    systemctl --user stop pulseaudio.socket && systemctl --user stop pulseaudio.service
    echo "Starting jack"
    qjackctl &
else
    echo "Invalid argument. Usage: $0 [start|stop]"
fi
