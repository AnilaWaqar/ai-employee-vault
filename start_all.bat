@echo off
title AI Employee — All Processes
echo Starting AI Employee processes via PM2...
cd /d E:\HC\AI_Employee_Vault
pm2 start ecosystem.config.js
pm2 status
pause
