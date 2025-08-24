#!/bin/bash
SVG_FILE="export2a.svg"
PNG_FILE="output.png"
DPI=300

inkscape "$SVG_FILE" --export-type=png --export-filename="$PNG_FILE" --export-dpi="$DPI"
