$python = "C:\Python314\python.exe"
$daily  = "E:\HC\AI_Employee_Vault\Skills\orchestrator\scripts\daily_briefing.py"
$weekly = "E:\HC\AI_Employee_Vault\Skills\orchestrator\scripts\weekly_audit.py"
$work   = "E:\HC\AI_Employee_Vault"

# Daily Briefing — 8AM
$a1 = New-ScheduledTaskAction -Execute $python -Argument "`"$daily`"" -WorkingDirectory $work
$t1 = New-ScheduledTaskTrigger -Daily -At "08:00AM"
$s1 = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 5) -RestartCount 2 -RestartInterval (New-TimeSpan -Minutes 1)
Unregister-ScheduledTask -TaskName "AI-Employee-Daily-Briefing" -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName "AI-Employee-Daily-Briefing" -Action $a1 -Trigger $t1 -Settings $s1 -Description "AI Employee daily briefing at 8AM" -RunLevel Limited -Force
Write-Host "[OK] Daily Briefing task registered."

# Weekly Audit — Sunday 10PM
$a2 = New-ScheduledTaskAction -Execute $python -Argument "`"$weekly`"" -WorkingDirectory $work
$t2 = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "10:00PM"
$s2 = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 10) -RestartCount 2 -RestartInterval (New-TimeSpan -Minutes 2)
Unregister-ScheduledTask -TaskName "AI-Employee-Weekly-Audit" -Confirm:$false -ErrorAction SilentlyContinue
Register-ScheduledTask -TaskName "AI-Employee-Weekly-Audit" -Action $a2 -Trigger $t2 -Settings $s2 -Description "AI Employee weekly audit every Sunday 10PM" -RunLevel Limited -Force
Write-Host "[OK] Weekly Audit task registered."

Write-Host ""
Write-Host "--- Registered Tasks ---"
Get-ScheduledTask -TaskName "AI-Employee-*" | Select-Object TaskName, State | Format-Table -AutoSize
