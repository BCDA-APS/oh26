#!/usr/bin/env bash

# Get the directory of the current script
SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" &> /dev/null && pwd)
cd "$SCRIPT_DIR" || exit 1

if [[ ! -f "image_000.jpg" ]]; then
    echo "No new jpg files found"
    exit 1
fi

# Generate the video
ffmpeg -framerate 5 -i image_%03d.jpg \
       -c:v libx264 -pix_fmt yuv420p output.mp4 || exit 1

# Find the next available directory to save to
n=0
while [ -d "scan$n" ]; do
    n=$((n + 1))
done

mkdir "scan$n"

# Move the images and generated video there
mv output.mp4 "scan$n.mp4"
mv "scan$n.mp4" "scan$n/"
mv *.jpg "scan$n/"
