#!/bin/bash
set -e

echo "Activating venv..."
source .venv/bin/activate

echo "Building yt-dlp-Simplified ..."
python -m nuitka ui.py --standalone --windows-console-mode=attach \
--enable-plugin=tk-inter \
--include-package-data=ttkthemes \
--windows-icon-from-ico=icon.ico \
--include-data-files=icon.ico=icon.ico \
--include-data-files=bins/*=bins/ \
--output-filename="yt-dlp-Simplified"

echo "Building updater ..."
python -m nuitka --standalone --onefile --windows-console-mode=attach \
--enable-plugin=tk-inter \
--output-filename="updater" self_updater.py

echo "Copying updater ..."
cp updater ./ui.dist/

echo "Build completed successfully."