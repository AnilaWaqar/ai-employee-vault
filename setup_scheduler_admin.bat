@echo off
title AI Employee — Task Scheduler Setup (Admin)
echo Requesting Administrator privileges...
powershell -Command "Start-Process cmd -ArgumentList '/c cd /d E:\HC\AI_Employee_Vault && C:\Python314\python.exe setup_scheduler.py && pause' -Verb RunAs"
