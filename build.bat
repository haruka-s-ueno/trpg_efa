@echo off
pushd %~dp0
echo This batch file marge efa_lite_full.html.
set /p strRtn="Do you want to continue?[y/n]"
if "%strRtn%" equ "y" (
  python build_efa_html.py
) else (
  echo Canceled.
)
pause
