@echo off
REM http://stackoverflow.com/questions/27649264/run-chrome-in-fullscreen-mode-on-windows
echo Step 1 of 2: Waiting a few seconds before starting the Kiosk...

"C:\windows\system32\ping" -n 5 -w 1000 127.0.0.1 >NUL

echo Step 2 of 5: Waiting a few more seconds before starting the browser...

"C:\windows\system32\ping" -n 5 -w 1000 127.0.0.1 >NUL

echo Final 'invisible' step: Starting the browser, Finally...

"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --chrome --kiosk http://192.168.1.1/frontend/ --incognito --disable-pinch --overscroll-history-navigation=0

exit