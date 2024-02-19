#!/bin/bash 

echo "systemctl --user stop pulseaudio.socket && systemctl --user stop pulseaudio.service"  
qjackctl &