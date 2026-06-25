#!/usr/bin/env bash

# Get the directory of the current script
SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" &> /dev/null && pwd)
cd "$SCRIPT_DIR" || exit 1

set -e           # Exit immediately if any command fails
set -o pipefail  # Ensure pipeline failures are captured

# If this fails, the script exits immediately
NEWEST_DIR=$(ls -td */ | head -n 1)

cd "$NEWEST_DIR"

VIDEO_FILE=$(ls *.mp4)
vlc "$VIDEO_FILE" >/dev/null 2>&1 &
