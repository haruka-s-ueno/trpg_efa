@echo off
pushd %~dp0
echo This batch file splits efa_lite.html.
set /p strRtn="Do you want to continue?[y/n]"
if "%strRtn%" equ "y" (
  python split_efa_html.py
) else (
  echo Canceled.
)
pause
