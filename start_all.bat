@echo off
title GovMesh Starter
echo Starting all GovMesh services...
powershell -ExecutionPolicy Bypass -File "%~dp0start_all.ps1"
