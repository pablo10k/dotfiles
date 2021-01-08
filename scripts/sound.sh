#!/bin/bash

# Configuration
#STEP="2"    # Anything you like.
#UNIT="dB"   # dB, %, etc.

# Set volume
#SETVOL="/usr/bin/amixer -qc 0 set Master"
VOLUME=$(awk -F"[][]" '/Left:/ { print $2 }' <(amixer sget Master))
echo $VOLUME
case "$1" in
    "up")
          amixer set Master 2%+
          ;;
  "down")
          amixer set Master 2%-
          ;;
  "mute")
		  
	      if [ $(awk -F"[][]" '/Left:/ { print $4 }' <(amixer sget Master)) != "on" ]; then
	      amixer set Master toggle
          volnoti-show $VOLUME
          else
          amixer set Master toggle
          volnoti-show -m
          
          fi
          exit 0
          ;;
esac

# Get current volume and state
VOLUME=$(awk -F"[][]" '/Left:/ { print $2 }' <(amixer sget Master))

volnoti-show $VOLUME

exit 0
