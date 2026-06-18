#!/usr/bin/env bash
ffmpeg -framerate 5 -i image_%03d.jpg -c:v libx264 -pix_fmt yuv420p ${1:-"output.mp4"}
