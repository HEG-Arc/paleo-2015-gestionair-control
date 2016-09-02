#!/bin/bash
export DISPLAY=:0.1
chromium-browser --kiosk --start-maximized  --incognito --disable-restore-background-contents --disable-translate --disable-new-tab-first-run http://192.168.1.1/game/frontend
