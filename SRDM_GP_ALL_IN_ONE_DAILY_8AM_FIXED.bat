@echo off
setlocal EnableExtensions DisableDelayedExpansion
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "SRDM_BAT=%~f0"
title SRDM GP e-Muster Work Type Update - CHECKED V5
echo SRDM CHECKED V5 - complete GP update and publication
set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar"
if exist "%~dp0.git" set "REPO=%~dp0."
if not exist "%REPO%\.git" (
 echo ERROR: Repository not found: %REPO%
 if /i not "%~1"=="--no-pause" pause
 exit /b 1
)
cd /d "%REPO%"
where py >nul 2>&1
if errorlevel 1 (set "PYTHON_CMD=python") else (set "PYTHON_CMD=py")
where %PYTHON_CMD% >nul 2>&1
if errorlevel 1 goto failed
if /i "%~1"=="--layout-only" goto run_update
if /i "%~1"=="--no-pause" goto run_update
echo Installing daily 8 AM India timer...
powershell.exe -NoProfile -ExecutionPolicy Bypass -EncodedCommand JABFAHIAcgBvAHIAQQBjAHQAaQBvAG4AUAByAGUAZgBlAHIAZQBuAGMAZQA9ACcAUwB0AG8AcAAnAAoAdAByAHkAIAB7AAoAIABpAGYAIAAoACgARwBlAHQALQBUAGkAbQBlAFoAbwBuAGUAKQAuAEkAZAAgAC0AbgBlACAAJwBJAG4AZABpAGEAIABTAHQAYQBuAGQAYQByAGQAIABUAGkAbQBlACcAKQAgAHsAdABoAHIAbwB3ACAAJwBTAGUAdAAgAFcAaQBuAGQAbwB3AHMAIAB0AGkAbQBlAHoAbwBuAGUAIAB0AG8AIABJAG4AZABpAGEAIABVAFQAQwArADAANQA6ADMAMAAgAGYAaQByAHMAdAAuACcAfQAKACAAJABmAG8AbABkAGUAcgA9AFsASQBPAC4AUABhAHQAaABdADoAOgBHAGUAdABGAHUAbABsAFAAYQB0AGgAKAAkAGUAbgB2ADoAUgBFAFAATwApAAoAIAAkAGIAYQB0AD0ASgBvAGkAbgAtAFAAYQB0AGgAIAAkAGYAbwBsAGQAZQByACAAJwBTAFIARABNAF8ARwBQAF8AQQBMAEwAXwBJAE4AXwBPAE4ARQBfAEQAQQBJAEwAWQBfADgAQQBNAC4AYgBhAHQAJwAKACAAaQBmACAAKABbAEkATwAuAFAAYQB0AGgAXQA6ADoARwBlAHQARgB1AGwAbABQAGEAdABoACgAJABlAG4AdgA6AFMAUgBEAE0AXwBCAEEAVAApACAALQBuAGUAIABbAEkATwAuAFAAYQB0AGgAXQA6ADoARwBlAHQARgB1AGwAbABQAGEAdABoACgAJABiAGEAdAApACkAIAB7AEMAbwBwAHkALQBJAHQAZQBtACAALQBMAGkAdABlAHIAYQBsAFAAYQB0AGgAIAAkAGUAbgB2ADoAUwBSAEQATQBfAEIAQQBUACAALQBEAGUAcwB0AGkAbgBhAHQAaQBvAG4AIAAkAGIAYQB0ACAALQBGAG8AcgBjAGUAfQAKACAAJABsAG8AZwA9AEoAbwBpAG4ALQBQAGEAdABoACAAJABmAG8AbABkAGUAcgAgACcAZwBwAC0AZQBtAHUAcwB0AGUAcgAtAGQAYQBpAGwAeQAtAHUAcABkAGEAdABlAC4AbABvAGcAJwAKACAAJABhAHIAZwBzAD0AJwAvAGQAIAAvAHMAIAAvAGMAIAAiACIAJwArACQAYgBhAHQAKwAnACIAIAAtAC0AbgBvAC0AcABhAHUAcwBlACAAPgA+ACAAIgAnACsAJABsAG8AZwArACcAIgAgADIAPgAmADEAIgAnAAoAIAAkAGEAYwB0AGkAbwBuAD0ATgBlAHcALQBTAGMAaABlAGQAdQBsAGUAZABUAGEAcwBrAEEAYwB0AGkAbwBuACAALQBFAHgAZQBjAHUAdABlACAAJABlAG4AdgA6AEMAbwBtAFMAcABlAGMAIAAtAEEAcgBnAHUAbQBlAG4AdAAgACQAYQByAGcAcwAgAC0AVwBvAHIAawBpAG4AZwBEAGkAcgBlAGMAdABvAHIAeQAgACQAZgBvAGwAZABlAHIACgAgACQAdAByAGkAZwBnAGUAcgA9AE4AZQB3AC0AUwBjAGgAZQBkAHUAbABlAGQAVABhAHMAawBUAHIAaQBnAGcAZQByACAALQBEAGEAaQBsAHkAIAAtAEEAdAAgACcAMAA4ADoAMAAwACcACgAgACQAcwBlAHQAdABpAG4AZwBzAD0ATgBlAHcALQBTAGMAaABlAGQAdQBsAGUAZABUAGEAcwBrAFMAZQB0AHQAaQBuAGcAcwBTAGUAdAAgAC0AUwB0AGEAcgB0AFcAaABlAG4AQQB2AGEAaQBsAGEAYgBsAGUAIAAtAFcAYQBrAGUAVABvAFIAdQBuACAALQBBAGwAbABvAHcAUwB0AGEAcgB0AEkAZgBPAG4AQgBhAHQAdABlAHIAaQBlAHMAIAAtAEQAbwBuAHQAUwB0AG8AcABJAGYARwBvAGkAbgBnAE8AbgBCAGEAdAB0AGUAcgBpAGUAcwAgAC0ATQB1AGwAdABpAHAAbABlAEkAbgBzAHQAYQBuAGMAZQBzACAASQBnAG4AbwByAGUATgBlAHcAIAAtAFIAZQBzAHQAYQByAHQAQwBvAHUAbgB0ACAAMwAgAC0AUgBlAHMAdABhAHIAdABJAG4AdABlAHIAdgBhAGwAIAAoAE4AZQB3AC0AVABpAG0AZQBTAHAAYQBuACAALQBNAGkAbgB1AHQAZQBzACAAMQAwACkAIAAtAEUAeABlAGMAdQB0AGkAbwBuAFQAaQBtAGUATABpAG0AaQB0ACAAKABOAGUAdwAtAFQAaQBtAGUAUwBwAGEAbgAgAC0ASABvAHUAcgBzACAAMwApAAoAIAAkAHAAcgBpAG4AYwBpAHAAYQBsAD0ATgBlAHcALQBTAGMAaABlAGQAdQBsAGUAZABUAGEAcwBrAFAAcgBpAG4AYwBpAHAAYQBsACAALQBVAHMAZQByAEkAZAAgACgAWwBTAGUAYwB1AHIAaQB0AHkALgBQAHIAaQBuAGMAaQBwAGEAbAAuAFcAaQBuAGQAbwB3AHMASQBkAGUAbgB0AGkAdAB5AF0AOgA6AEcAZQB0AEMAdQByAHIAZQBuAHQAKAApAC4ATgBhAG0AZQApACAALQBMAG8AZwBvAG4AVAB5AHAAZQAgAEkAbgB0AGUAcgBhAGMAdABpAHYAZQAgAC0AUgB1AG4ATABlAHYAZQBsACAATABpAG0AaQB0AGUAZAAKACAAUgBlAGcAaQBzAHQAZQByAC0AUwBjAGgAZQBkAHUAbABlAGQAVABhAHMAawAgAC0AVABhAHMAawBOAGEAbQBlACAAJwBTAFIARABNACAARwBQACAAZQBNAHUAcwB0AGUAcgAgAFcAbwByAGsAIABUAHkAcABlAHMAIAAtACAARABhAGkAbAB5ACAAOABBAE0AJwAgAC0AQQBjAHQAaQBvAG4AIAAkAGEAYwB0AGkAbwBuACAALQBUAHIAaQBnAGcAZQByACAAJAB0AHIAaQBnAGcAZQByACAALQBTAGUAdAB0AGkAbgBnAHMAIAAkAHMAZQB0AHQAaQBuAGcAcwAgAC0AUAByAGkAbgBjAGkAcABhAGwAIAAkAHAAcgBpAG4AYwBpAHAAYQBsACAALQBGAG8AcgBjAGUAIAB8ACAATwB1AHQALQBOAHUAbABsAAoAIAAkAGkAbgBmAG8APQBHAGUAdAAtAFMAYwBoAGUAZAB1AGwAZQBkAFQAYQBzAGsASQBuAGYAbwAgAC0AVABhAHMAawBOAGEAbQBlACAAJwBTAFIARABNACAARwBQACAAZQBNAHUAcwB0AGUAcgAgAFcAbwByAGsAIABUAHkAcABlAHMAIAAtACAARABhAGkAbAB5ACAAOABBAE0AJwAKACAAVwByAGkAdABlAC0ASABvAHMAdAAgACgAJwBTAFUAQwBDAEUAUwBTADoAIABEAGEAaQBsAHkAIAA4ACAAQQBNACAAdABpAG0AZQByACAAaQBuAHMAdABhAGwAbABlAGQALgAgAE4AZQB4AHQAIAByAHUAbgA6ACAAJwArACQAaQBuAGYAbwAuAE4AZQB4AHQAUgB1AG4AVABpAG0AZQApAAoAIABXAHIAaQB0AGUALQBIAG8AcwB0ACAAKAAnAEwAbwBnADoAIAAnACsAJABsAG8AZwApAAoAIABlAHgAaQB0ACAAMAAKAH0AIABjAGEAdABjAGgAIAB7AFcAcgBpAHQAZQAtAEgAbwBzAHQAIAAoACcAVABJAE0ARQBSACAARQBSAFIATwBSADoAIAAnACsAJABfAC4ARQB4AGMAZQBwAHQAaQBvAG4ALgBNAGUAcwBzAGEAZwBlACkAOwAgAGUAeABpAHQAIAAxAH0ACgA=
if errorlevel 1 goto failed
:run_update
%PYTHON_CMD% -c "import base64; exec(base64.b64decode('aW1wb3J0IHBhdGhsaWIscmUsYmFzZTY0LHN5cyxzdWJwcm9jZXNzLHRlbXBmaWxlCnJlcG89cGF0aGxpYi5QYXRoLmN3ZCgpCnQ9cGF0aGxpYi5QYXRoKHN5cy5hcmd2WzFdKS5yZWFkX3RleHQoZW5jb2Rpbmc9InV0Zi04IikKY29udGVudD1iYXNlNjQuYjY0ZGVjb2RlKHJlLnNlYXJjaChyIlJFTSBTUkRNX1VJX1BBWUxPQUQgKFtBLVphLXowLTkrLz1dKykiLHQpWzFdKQpkZWYgcnVuKGEsYz1yZXBvKTpzdWJwcm9jZXNzLnJ1bihhLGN3ZD1jLGNoZWNrPVRydWUpCnJ1bihbImdpdCIsImZldGNoIiwib3JpZ2luIiwibWFpbiJdKQp3PXBhdGhsaWIuUGF0aCh0ZW1wZmlsZS5ta2R0ZW1wKHByZWZpeD0ic3JkbS1sYXlvdXQtIikpO3cucm1kaXIoKQpydW4oWyJnaXQiLCJ3b3JrdHJlZSIsImFkZCIsIi0tZGV0YWNoIixzdHIodyksIkZFVENIX0hFQUQiXSkKdHJ5OgogKHcvImdwLWxhYm91ci1tdXN0ZXItbW9kdWxlLmpzIikud3JpdGVfYnl0ZXMoY29udGVudCkKIHJ1bihbImdpdCIsImFkZCIsIi0tIiwiZ3AtbGFib3VyLW11c3Rlci1tb2R1bGUuanMiXSx3KQogcmVzdWx0PXN1YnByb2Nlc3MucnVuKFsiZ2l0IiwiZGlmZiIsIi0tY2FjaGVkIiwiLS1xdWlldCJdLGN3ZD13KS5yZXR1cm5jb2RlCiBpZiByZXN1bHQ9PTE6CiAgcnVuKFsiZ2l0IiwiY29tbWl0IiwiLW0iLCJVcGRhdGUgY29tcGFjdCByZXBvcnQgbGF5b3V0IGFuZCBjb2xvciBpbmRpY2F0b3JzIl0sdykKICBydW4oWyJnaXQiLCJwdXNoIiwib3JpZ2luIiwiSEVBRDptYWluIl0sdykKIGVsaWYgcmVzdWx0IT0wOnJhaXNlIFJ1bnRpbWVFcnJvcigiR2l0IGRpZmYgZmFpbGVkIikKIHByaW50KCJTVUNDRVNTOiBMYXlvdXQgcHVibGlzaGVkOyBleGlzdGluZyBvbmxpbmUgZGF0YSByZXRhaW5lZC4gUmVmcmVzaCBDdHJsK1NoaWZ0K1IuIikKZmluYWxseTpydW4oWyJnaXQiLCJ3b3JrdHJlZSIsInJlbW92ZSIsc3RyKHcpXSkK'))" "%~f0"
if errorlevel 1 goto failed
if /i "%~1"=="--layout-only" exit /b 0
echo START: %DATE% %TIME%
if not exist scripts_local mkdir scripts_local
echo Installing corrected Work Type parser...
%PYTHON_CMD% -c "import pathlib,sys; p=pathlib.Path(sys.argv[1]); data=p.read_text(encoding='utf-8').split(chr(35)+' SRDM_EMBEDDED_UPDATER',1)[1]; compile(data,'update_gp_emuster.py','exec'); pathlib.Path('scripts_local/update_gp_emuster.py').write_text(data,encoding='utf-8')" "%~f0"
if errorlevel 1 goto failed
%PYTHON_CMD% -c "import playwright"
if errorlevel 1 (
 %PYTHON_CMD% -m pip install playwright
 if errorlevel 1 goto failed
)
%PYTHON_CMD% -m playwright install chromium
if errorlevel 1 goto failed
set "SRDM_REPAIR="
if /i "%~1"=="--repair-missing" set "SRDM_REPAIR=--repair-missing"
echo Reading corrected 8-Janpad summary source, then GP and column 6 work lists...
%PYTHON_CMD% scripts_local\update_gp_emuster.py %SRDM_REPAIR% --headed --url "https://vbgramgrep.dord.gov.in/VBGRAMG/dpc_sms_new.aspx?payload=c_dCXx6L-IMkcEdlRICw87o-OWrumZUuTOVJCtXMwo49VCcKVJKknrfE_4qO0AT_WQTG3yWM7D1kNUU7DSpTx1H8j3SYUjwu3q4dQX_CfBdu4ni8Iou1EYozxNZb5rwNvD2JMp78Hx-qNCdsq3ux6X1MITBA5uUF3gtds07lUIHnl4ONcwgjtjtzvWYQ0UDGVInRFjvVbtwWWXI7s8-I3jU8QwBBMeYwU7dbbckRQbgR_S8b6XGjuQ6EwEUi4ba3pW06r3n-L-iVwCLbYfyloXs1UzJGGw9YBlOFBm-hlzE"
if errorlevel 1 goto failed
%PYTHON_CMD% -c "import pathlib,re,base64,sys; t=pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'); pathlib.Path('gp-labour-muster-module.js').write_bytes(base64.b64decode(re.search(r'REM SRDM_UI_PAYLOAD ([A-Za-z0-9+/=]+)',t)[1]))" "%~f0"
if errorlevel 1 goto failed
git fetch origin main
if errorlevel 1 goto failed
set "PUBLISH_DIR=%TEMP%\SRDM_GP_EMUSTER_%RANDOM%_%RANDOM%"
git worktree add --detach "%PUBLISH_DIR%" origin/main
if errorlevel 1 goto failed
copy /y gp-emuster-data.js "%PUBLISH_DIR%\gp-emuster-data.js" >nul
if errorlevel 1 goto failed
copy /y gp-labour-muster-module.js "%PUBLISH_DIR%\gp-labour-muster-module.js" >nul
if errorlevel 1 goto failed
git -C "%PUBLISH_DIR%" add -- gp-emuster-data.js gp-labour-muster-module.js
if errorlevel 1 goto failed
git -C "%PUBLISH_DIR%" diff --cached --quiet
if errorlevel 2 goto failed
if not errorlevel 1 goto unchanged
git -C "%PUBLISH_DIR%" commit -m "Update GP data and consolidated report layout"
if errorlevel 1 goto failed
git -C "%PUBLISH_DIR%" push origin HEAD:main
if errorlevel 1 goto failed
git worktree remove "%PUBLISH_DIR%"
echo SUCCESS: Verified GP and work-type data published. Refresh site with Ctrl+Shift+R.
if /i not "%~1"=="--no-pause" pause
exit /b 0
:unchanged
git worktree remove "%PUBLISH_DIR%"
echo SUCCESS: Verified data is already current.
if /i not "%~1"=="--no-pause" pause
exit /b 0
:failed
echo ERROR: Update incomplete. Previous online data retained. Share the error shown above.
if /i not "%~1"=="--no-pause" pause
exit /b 1

REM SRDM_UI_PAYLOAD KGZ1bmN0aW9uKCl7CmNvbnN0IG1lcmdlZENhdGVnb3J5PXQ9PlsnSUFZIEhvdXNlcycsJ1BNQVkgRycsJ1BNQVktRyddLmluY2x1ZGVzKFN0cmluZyh0KS50cmltKCkpPydQTUFZLUcnOnQ7CmNvbnN0IHRpdGxlPSfgpIngpKrgpK/gpILgpKTgpY3gpLDgpYAv4KS44KWH4KSV4KWN4KSf4KSw4KS14KS+4KSwIOCkleCkvuCksOCljeCkry3gpLbgpY3gpLDgpYfgpKPgpYDgpLXgpL7gpLAg4oCUIOCkquCljeCksOCkl+CkpOCkv+CksOCkpCDgpJXgpL7gpLDgpY3gpK8sIE1SIOCknOCkvuCksOClgCDgpJXgpL7gpLDgpY3gpK8g4KSP4KS14KSCIOCkuOCkguCksuCkl+CljeCkqCDgpLbgpY3gpLDgpK7gpL/gpJUnOwpsZXQgYm94OwpmdW5jdGlvbiBkcmF3KCl7CiBpZighYm94KXtib3g9ZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgnc2VjdGlvbicpO2JveC5pZD0nZ3BMYWJvdXJNdXN0ZXJNb2R1bGUnO2JveC5zdHlsZS5jc3NUZXh0PSdtYXJnaW46MTZweCAwO3BhZGRpbmc6MTZweDtib3JkZXI6MnB4IHNvbGlkICMxNDU4OGM7Ym9yZGVyLXJhZGl1czoxMnB4O2JhY2tncm91bmQ6I2ZmZjtjb2xvcjojMTAyYjQ2Jztkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgncmVwb3J0VGFibGUnKS5wYXJlbnRFbGVtZW50Lmluc2VydEFkamFjZW50RWxlbWVudCgnYWZ0ZXJlbmQnLGJveCk7fQogYm94LmhpZGRlbj12aWV3IT09J29mZmljaWFsJztpZihib3guaGlkZGVuKXJldHVybjsKIGNvbnN0IGxpdmU9d2luZG93LkdQX1dPUktfVFlQRV9NVVNURVJfUkVQT1JUOwogY29uc3QgdG9kYXk9bmV3IEludGwuRGF0ZVRpbWVGb3JtYXQoJ2VuLUdCJyx7dGltZVpvbmU6J0FzaWEvS29sa2F0YScsZGF5OicyLWRpZ2l0Jyxtb250aDonMi1kaWdpdCcseWVhcjonbnVtZXJpYyd9KS5mb3JtYXQobmV3IERhdGUoKSkucmVwbGFjZUFsbCgnLycsJy0nKTsKIGNvbnN0IGFjdHVhbD1uZXcgTWFwKCk7Zm9yKGNvbnN0IHIgb2YgbGl2ZT8ucm93c3x8W10pe2NvbnN0IGo9bm9ybUphbnBhZChyLmphbnBhZCk7aWYoIWFjdHVhbC5oYXMoaikpYWN0dWFsLnNldChqLHtsYWJvdXI6MCx3b3JrczowLGdwczowfSk7Y29uc3QgYT1hY3R1YWwuZ2V0KGopO2EubGFib3VyKz1OdW1iZXIoci5sYWJvdXIpO2Eud29ya3MrPU51bWJlcihyLndvcmtzTVIpO2EuZ3BzKys7fQogY29uc3QgbWlzbWF0Y2g9KG9mZmljaWFsfHxbXSkuZmlsdGVyKHI9Pntjb25zdCBhPWFjdHVhbC5nZXQobm9ybUphbnBhZChyLmphbnBhZCkpO3JldHVybiAhYXx8YS5sYWJvdXIhPT1OdW1iZXIoci5sYWJvdXJBbGwpfHxhLndvcmtzIT09TnVtYmVyKHIubXJBbGwpfHxhLmdwcyE9PU51bWJlcihyLnRvdGFsR1ApO30pOwogaWYoIWxpdmV8fGxpdmUuZGF0ZSE9PXRvZGF5fHxtaXNtYXRjaC5sZW5ndGgpe2JveC5pbm5lckhUTUw9JzxoMj4nK3RpdGxlKyc8L2gyPjxwIHN0eWxlPSJjb2xvcjojYjkxYzFjO2ZvbnQtd2VpZ2h0OjgwMCI+R1AgLyDgpJXgpL7gpLDgpY3gpK8t4KSq4KWN4KSw4KSV4KS+4KSwIOCkoeClh+Ckn+CkviDgpJXgpL4g4KSG4KScIOCkleClgCDgpJzgpKjgpKrgpKYg4KSw4KS/4KSq4KWL4KSw4KWN4KSfIOCkuOClhyDgpK7gpL/gpLLgpL7gpKgg4KSy4KSC4KSs4KS/4KSkIOCkueCliOClpCBHUCDgpKHgpYfgpJ/gpL4g4KSV4KWAIOCkpOCkv+CkpeCkvzogJytlc2MobGl2ZT8uZGF0ZXx8J+CkheCkqOClgeCkquCksuCkrOCljeCkpycpKyfgpaQgJytlc2MobWlzbWF0Y2gubWFwKHI9Pm5vcm1KYW5wYWQoci5qYW5wYWQpKS5qb2luKCcsICcpKSsn4KWkIOCkheCkquCkoeClh+CknyBCQVQg4KSa4KSy4KS+4KSP4KSB4KWkPC9wPic7cmV0dXJuO30KIGNvbnN0IHNvdXJjZURhdGE9bGl2ZSYmQXJyYXkuaXNBcnJheShsaXZlLnJvd3MpP2ZpbHRlclJvd3MobGl2ZS5yb3dzKTpmaWx0ZXJlZFJvd3MoKTsKIGNvbnN0IGRhdGE9c29ydFJvd3Moc291cmNlRGF0YSwnbGFib3VyJyxbJ2phbnBhZCcsJ3BhbmNoYXlhdCddKTsKIGNvbnN0IGRhdGU9bGl2ZT8uZGF0ZXx8YXV0b01ldGE/LnNvdXJjZURhdGVzPy5SZXBEYXl8fGV4dHJhY3REYXRlKHJlcG9ydFRpdGxlKXx8J+CkpOCkv+CkpeCkvyDgpIngpKrgpLLgpKzgpY3gpKcg4KSo4KS54KWA4KSCJzsKIGNvbnN0IGJhbmRzPVtbMCwwLCfgpLbgpYLgpKjgpY3gpK8nXSxbMSwxLCcwMSddLFsyLDIsJzAyJ10sWzMsMywnMDMnXSxbNCw0LCcwNCddLFs1LDUsJzA1J10sWzYsMTAsJzA2IOCkuOClhyAxMCddLFsxMSwyMCwnMTEg4KS44KWHIDIwJ10sWzIxLDMwLCcyMSDgpLjgpYcgMzAnXSxbMzEsNTAsJzMxIOCkuOClhyA1MCddLFs1MSwxMDAsJzUxIOCkuOClhyAxMDAnXSxbMTAxLEluZmluaXR5LCcxMDAg4KS44KWHIOCkheCkp+Ckv+CklSddXTsKIGNvbnN0IHdvcmtUeXBlcz1bLi4ubmV3IFNldChbJ0Ftcml0IFNhcm92YXInLC4uLihsaXZlPy53b3JrQ2F0ZWdvcmllc3x8W10pLm1hcChtZXJnZWRDYXRlZ29yeSksLi4ub25nb2luZ0RldGFpbHMubWFwKHI9Pm1lcmdlZENhdGVnb3J5KHIuZmluYWxDYXRlZ29yeXx8J090aGVyIFdvcmtzJykpXSldLnNvcnQoKGEsYik9PmEubG9jYWxlQ29tcGFyZShiLCdlbicpKTsKIGlmKCF3b3JrVHlwZXMubGVuZ3RoKXdvcmtUeXBlcy5wdXNoKCdQTUFZLUcnLCdDZW1lbnQgQ29uY3JldGUnLCdHcmF2ZWwgUm9hZCcsJ1BsYXkgRmllbGQnLCdGYXJtIFBvbmQnLCdXYXRlcnNoZWQgUmVsYXRlZCBXb3JrcycsJ1dhdGVyIGNvbnNlcnZhdGlvbiAmIHJlY2hhcmdlJywnRWsgQmFnaXlhJywnR2FwIEZpbGxpbmcgaW4gUGxhbnRhdGlvbicsJ090aGVyIFdvcmtzJyk7CiAvLyBDb3VudCBpc3N1ZWQtTVIgd29ya3MgZnJvbSBjb2x1bW4gNiBkcmlsbC1kb3duIGJ5IHdvcmsgdHlwZTsgZG8gbm90IHVzZSBtdXN0ZXIgcm9sbCB0b3RhbHMuCiBjb25zdCBzb3VyY2U9d2luZG93LkdQX1dPUktfVFlQRV9NVVNURVJfUkVQT1JUOwogY29uc3Qgc291cmNlUm93cz1zb3VyY2UmJkFycmF5LmlzQXJyYXkoc291cmNlLnJvd3MpP3NvdXJjZS5yb3dzOltdOwogY29uc3QgZ3BLZXk9cj0+bm9ybUphbnBhZChyLmphbnBhZCkrJ8KmJytjbGVhbihyLnBhbmNoYXlhdCkudG9VcHBlckNhc2UoKS5yZXBsYWNlKC9bXkEtWjAtOVx1MDkwMC1cdTA5N2ZdL2csJycpOwogY29uc3Qgb2ZmaWNpYWxXb3JrQ291bnRzPW5ldyBNYXAoc291cmNlUm93cy5tYXAocj0+W2dwS2V5KHIpLHJdKSk7CiBjb25zdCBvbmdvaW5nQnlHUD1uZXcgTWFwKCksb25nb2luZ1R5cGVzQnlHUD1uZXcgTWFwKCksc2Vlbk9uZ29pbmdDb2Rlcz1uZXcgU2V0KCk7CiBmb3IoY29uc3Qgd29yayBvZiBvbmdvaW5nRGV0YWlscyl7CiAgaWYoIXdvcmsuY29kZXx8c2Vlbk9uZ29pbmdDb2Rlcy5oYXMod29yay5jb2RlKSljb250aW51ZTsKICBzZWVuT25nb2luZ0NvZGVzLmFkZCh3b3JrLmNvZGUpOwogIGNvbnN0IGs9Z3BLZXkod29yayk7b25nb2luZ0J5R1Auc2V0KGssKG9uZ29pbmdCeUdQLmdldChrKXx8MCkrMSk7CiAgaWYoIW9uZ29pbmdUeXBlc0J5R1AuaGFzKGspKW9uZ29pbmdUeXBlc0J5R1Auc2V0KGsse30pO2NvbnN0IHR5cGVzPW9uZ29pbmdUeXBlc0J5R1AuZ2V0KGspO2NvbnN0IHR5cGU9bWVyZ2VkQ2F0ZWdvcnkod29yay5maW5hbENhdGVnb3J5fHx3b3JrLmNhdGVnb3J5fHwnT3RoZXIgV29ya3MnKTt0eXBlc1t0eXBlXT0odHlwZXNbdHlwZV18fDApKzE7CiB9CiBjb25zdCBncm91cHM9bmV3IE1hcCgpLHNlZW49bmV3IFNldCgpOwogZm9yKGNvbnN0IHIgb2YgZGF0YSl7CiBjb25zdCBrZXk9bm9ybUphbnBhZChyLmphbnBhZCkrJ8KmJytjbGVhbihyLnBhbmNoYXlhdCkudG9VcHBlckNhc2UoKTsKIGlmKHNlZW4uaGFzKGtleSkpY29udGludWU7c2Vlbi5hZGQoa2V5KTsKIGNvbnN0IGo9bm9ybUphbnBhZChyLmphbnBhZCk7CiBjb25zdCBlbmdpbmVlcj1jbGVhbihyLmVuZ2luZWVyKXx8J+CkqOCkvuCkriDgpIngpKrgpLLgpKzgpY3gpKcg4KSo4KS54KWA4KSCJyxzZWN0b3I9Y2xlYW4oci5jbHVzdGVyKXx8J+CkuOClh+CkleCljeCkn+CksCDgpIngpKrgpLLgpKzgpY3gpKcg4KSo4KS54KWA4KSCJzsKIGNvbnN0IGdyb3VwS2V5PVtqLGVuZ2luZWVyLHNlY3Rvcl0uam9pbignwqYnKTsKIGlmKCFncm91cHMuaGFzKGdyb3VwS2V5KSlncm91cHMuc2V0KGdyb3VwS2V5LHtqYW5wYWQ6aixlbmdpbmVlcixzZWN0b3IsdG90YWw6MCxvbmdvaW5nOjAsaXNzdWVkVG90YWw6MCxpc3N1ZWRNaXNzaW5nOmZhbHNlLHdvcmtpbmdHUDowLGNvdW50czpiYW5kcy5tYXAoKCk9PjApLG1pc3Npbmc6MCxvbmdvaW5nQ291bnRzOndvcmtUeXBlcy5tYXAoKCk9PjApLHdvcmtDb3VudHM6d29ya1R5cGVzLm1hcCgoKT0+MCksd29ya01pc3Npbmc6d29ya1R5cGVzLm1hcCgoKT0+ZmFsc2UpfSk7CiBjb25zdCBnPWdyb3Vwcy5nZXQoZ3JvdXBLZXkpO2cudG90YWwrKztnLm9uZ29pbmcrPW9uZ29pbmdCeUdQLmdldChncEtleShyKSl8fDA7CiBjb25zdCB3b3JrUm93PW9mZmljaWFsV29ya0NvdW50cy5nZXQoZ3BLZXkocikpOwogY29uc3QgaXNzdWVkQ291bnQ9d29ya1Jvdz8ud29ya3NNUjsKIGlmKGlzc3VlZENvdW50PT09bnVsbHx8aXNzdWVkQ291bnQ9PT11bmRlZmluZWR8fCFOdW1iZXIuaXNJbnRlZ2VyKE51bWJlcihpc3N1ZWRDb3VudCkpfHxOdW1iZXIoaXNzdWVkQ291bnQpPDApZy5pc3N1ZWRNaXNzaW5nPXRydWU7CiBlbHNlIGcuaXNzdWVkVG90YWwrPU51bWJlcihpc3N1ZWRDb3VudCk7CiB3b3JrVHlwZXMuZm9yRWFjaCgodHlwZSxpKT0+ewogZy5vbmdvaW5nQ291bnRzW2ldKz1vbmdvaW5nVHlwZXNCeUdQLmdldChncEtleShyKSk/Llt0eXBlXXx8MDsKIGNvbnN0IHJhdz13b3JrUm93Py5pc3N1ZWRXb3JrczsKIGNvbnN0IHY9dHlwZT09PSdQTUFZLUcnJiZyYXc/WydQTUFZLUcnLCdQTUFZIEcnLCdJQVkgSG91c2VzJ10ucmVkdWNlKChzdW0sayk9PnN1bStOdW1iZXIocmF3W2tdPz8wKSwwKTpyYXc/KHJhd1t0eXBlXT8/MCk6dW5kZWZpbmVkOwogaWYodj09PW51bGx8fHY9PT11bmRlZmluZWR8fHY9PT0nJ3x8IU51bWJlci5pc0ludGVnZXIoTnVtYmVyKHYpKXx8TnVtYmVyKHYpPDApZy53b3JrTWlzc2luZ1tpXT10cnVlOwogZWxzZSBnLndvcmtDb3VudHNbaV0rPU51bWJlcih2KTsKIH0pOwogY29uc3Qgbj1yLmxhYm91cj09PW51bGx8fHIubGFib3VyPT09dW5kZWZpbmVkfHxjbGVhbihyLmxhYm91cik9PT0nJz9OYU46TnVtYmVyKHIubGFib3VyKTsKIGNvbnN0IGJpPU51bWJlci5pc0ludGVnZXIobikmJm4+PTA/YmFuZHMuZmluZEluZGV4KGI9Pm4+PWJbMF0mJm48PWJbMV0pOi0xOwogaWYoYmk8MClnLm1pc3NpbmcrKztlbHNlIHtnLmNvdW50c1tiaV0rKztpZihuPjApZy53b3JraW5nR1ArKzt9CiB9CiBjb25zdCBzdW1tYXJ5PVsuLi5ncm91cHMudmFsdWVzKCldLnNvcnQoKGEsYik9PmEuamFucGFkLmxvY2FsZUNvbXBhcmUoYi5qYW5wYWQsJ2hpJyl8fGEuZW5naW5lZXIubG9jYWxlQ29tcGFyZShiLmVuZ2luZWVyLCdoaScpfHxhLnNlY3Rvci5sb2NhbGVDb21wYXJlKGIuc2VjdG9yLCdoaScpKTsKIGNvbnN0IGhhc01pc3Npbmc9c3VtbWFyeS5zb21lKGc9PmcubWlzc2luZz4wKTsKIGNvbnN0IGhlYWRlcnM9WyfgpJzgpKjgpKrgpKYg4KSV4KS+IOCkqOCkvuCkricsJ+CkieCkquCkr+CkguCkpOCljeCksOClgCDgpJXgpL4g4KSo4KS+4KSuL+CkuOClh+CkleCljeCkn+CksCDgpJXgpL4g4KSo4KS+4KSuJywn4KSV4KWB4KSyIOCkquCljeCksOCkreCkvuCksCDgpJXgpYAg4KSX4KWN4KSw4KS+4KSuIOCkquCkguCkmuCkvuCkr+CkpCcsJ+CktuCljeCksOCkruCkv+CklSDgpLjgpILgpLLgpJfgpY3gpKggR1BzJywuLi5iYW5kcy5tYXAoYj0+YlsyXSsnIOCktuCljeCksOCkruCkv+CklSDgpLXgpL7gpLLgpYAgR1BzJyksLi4uKGhhc01pc3Npbmc/WyfgpLbgpY3gpLDgpK7gpL/gpJUg4KSh4KWH4KSf4KS+IOCkheCkqOClgeCkquCksuCkrOCljeCkpyBHUHMnXTpbXSksLi4ud29ya1R5cGVzLmZsYXRNYXAodD0+dD09PSdBbXJpdCBTYXJvdmFyJz9bJ+CkruCkuOCljeCkn+CksCDgpLDgpYvgpLIg4KSc4KS+4KSw4KWAIOCkleCkvuCksOCljeCkr+Cli+CkgiDgpJXgpYAg4KSV4KWB4KSyIOCkuOCkguCkluCljeCkr+CkviAvIOCkleClgeCksiDgpKrgpY3gpLDgpJfgpKTgpL/gpLDgpKQg4KSV4KS+4KSw4KWN4KSvJyx0XTpbdF0pXTsKIGNvbnN0IGNvbHVtbldpZHRocz1oZWFkZXJzLm1hcCgoeCxpKT0+aT09PTA/OTU6aT09PTE/MjQwOmk9PT0yPzYwOmk9PT0zPzYwOmk8NCtiYW5kcy5sZW5ndGg/NDg6eC5pbmNsdWRlcygn4KSu4KS44KWN4KSf4KSwIOCksOCli+CksiDgpJzgpL7gpLDgpYAg4KSV4KS+4KSw4KWN4KSv4KWL4KSCIOCkleClgCDgpJXgpYHgpLIg4KS44KSC4KSW4KWN4KSv4KS+Jyk/MTEwOjc2KTsKIGxldCB0YWJsZT0nPHRhYmxlIHN0eWxlPSJ3aWR0aDonK2NvbHVtbldpZHRocy5yZWR1Y2UoKGEsYik9PmErYiwwKSsncHg7dGFibGUtbGF5b3V0OmZpeGVkO2JvcmRlci1jb2xsYXBzZTpjb2xsYXBzZSI+PGNvbGdyb3VwPicrY29sdW1uV2lkdGhzLm1hcCh3PT4nPGNvbCBzdHlsZT0id2lkdGg6Jyt3KydweCI+Jykuam9pbignJykrJzwvY29sZ3JvdXA+PHRoZWFkPjx0cj4nK2hlYWRlcnMubWFwKCh4LGkpPT4nPHRoJysoaT09PTI/JyBzdHlsZT0id2lkdGg6NjBweDttaW4td2lkdGg6NjBweDttYXgtd2lkdGg6NjBweDt3aGl0ZS1zcGFjZTpub3JtYWwiJzp4LmluY2x1ZGVzKCfgpK7gpLjgpY3gpJ/gpLAg4KSw4KWL4KSyIOCknOCkvuCksOClgCDgpJXgpL7gpLDgpY3gpK/gpYvgpIIg4KSV4KWAIOCkleClgeCksiDgpLjgpILgpJbgpY3gpK/gpL4nKT8nIHN0eWxlPSJiYWNrZ3JvdW5kOiMxNTgwM2Q7Y29sb3I6I2ZmZjtmb250LXdlaWdodDo5MDAiJzonJykrJz4nKyhpPT09Mj8n4KSV4KWB4KSyIOCkquCljeCksOCkreCkvuCksCDgpJXgpYA8YnI+4KSX4KWN4KSw4KS+4KSuIOCkquCkguCkmuCkvuCkr+CkpCc6ZXNjKHgpKSsnPC90aD4nKS5qb2luKCcnKSsnPC90cj48L3RoZWFkPjx0Ym9keT4nOwogY29uc3QgcGFpcj0oZyxpKT0+ewogY29uc3QgbXI9Zy53b3JrQ291bnRzW2ldLG9uZ29pbmc9Zy5vbmdvaW5nQ291bnRzW2ldLG1pc3Npbmc9Zy53b3JrTWlzc2luZ1tpXTsKIGNvbnN0IHZhbHVlPWZtdChtcikrKG1pc3Npbmc/JyonOicnKSsnIC8gJytmbXQob25nb2luZyk7CiBpZihtaXNzaW5nKXJldHVybiAnPHNwYW4gc3R5bGU9ImZvbnQtd2VpZ2h0OjkwMDtjb2xvcjojOWEzNDEyIiB0aXRsZT0iJytlc2MoJ+CkleCkriDgpLjgpYcg4KSV4KSuICcrZm10KG1yKSsnIOCkleCkvuCksOCljeCkr+Cli+CkgiDgpK7gpYfgpIIgTVIg4KSc4KS+4KSw4KWAIOCkueCliOClpCDgpJXgpYHgpJsgR1Ag4KSV4KS+IOCkleCkvuCksOCljeCkry3gpKrgpY3gpLDgpJXgpL7gpLAg4KS14KS/4KS14KSw4KSjIOCkheCkqOClgeCkquCksuCkrOCljeCkpyDgpLngpYg7IOCkr+CkuSDgpKrgpYLgpLDgpY3gpKMg4KSV4KWB4KSyIOCkqOCkueClgOCkgiDgpLngpYjgpaQnKSsnIj4nK3ZhbHVlKyc8L3NwYW4+JzsKIGNvbnN0IGdhcD1NYXRoLm1heCgwLG9uZ29pbmctbXIpOwogY29uc3QgY2xzPW9uZ29pbmc+MCYmbXI9PT0wPydtci1ub25lJzpnYXA+MD8nbXItZ2FwJzonbXItb2snOwogY29uc3QgaGludD1vbmdvaW5nPjAmJm1yPT09MD8nTVIg4KSc4KS+4KSw4KWAIOCkqOCkueClgOCkgic6Z2FwPjA/J01SIOCksOCkueCkv+CkpDogJytmbXQoZ2FwKTonJzsKIHJldHVybiAnPHNwYW4gY2xhc3M9IicrY2xzKyciIHRpdGxlPSInK2VzYyhoaW50fHwnTVIg4KSc4KS+4KSw4KWAIOCkleCkvuCksOCljeCkryAvIOCkleClgeCksiDgpKrgpY3gpLDgpJfgpKTgpL/gpLDgpKQg4KSV4KS+4KSw4KWN4KSvJykrJyI+Jyt2YWx1ZSsnPC9zcGFuPic7CiB9OwogY29uc3QgY2VsbHM9Zz0+W2cudG90YWwsZy53b3JraW5nR1AsLi4uZy5jb3VudHMsLi4uKGhhc01pc3Npbmc/W2cubWlzc2luZ106W10pXS5tYXAodj0+Jzx0ZCBzdHlsZT0iZm9udC13ZWlnaHQ6ODAwO3RleHQtYWxpZ246Y2VudGVyIj4nK2ZtdCh2KSsnPC90ZD4nKS5qb2luKCcnKSt3b3JrVHlwZXMubWFwKCh0eXBlLGkpPT4odHlwZT09PSdBbXJpdCBTYXJvdmFyJz8nPHRkIHN0eWxlPSJmb250LXdlaWdodDo4MDA7dGV4dC1hbGlnbjpjZW50ZXI7d2hpdGUtc3BhY2U6bm93cmFwO2NvbG9yOiMxNTgwM2Q7YmFja2dyb3VuZDojZWNmZGY1O2ZvbnQtd2VpZ2h0OjkwMCI+JysoZy5pc3N1ZWRNaXNzaW5nPyfigJQnOmZtdChnLmlzc3VlZFRvdGFsKSkrJyAvICcrZm10KGcub25nb2luZykrJzwvdGQ+JzonJykrJzx0ZCBzdHlsZT0iZm9udC13ZWlnaHQ6ODAwO3RleHQtYWxpZ246Y2VudGVyIj4nK3BhaXIoZyxpKSsnPC90ZD4nKS5qb2luKCcnKTsKIGNvbnN0IGphbnBhZHM9Wy4uLm5ldyBTZXQoc3VtbWFyeS5tYXAoZz0+Zy5qYW5wYWQpKV07CiBmb3IoY29uc3QgamFucGFkIG9mIGphbnBhZHMpewogY29uc3QgZW50cmllcz1zdW1tYXJ5LmZpbHRlcihnPT5nLmphbnBhZD09PWphbnBhZCk7CiB0YWJsZSs9ZW50cmllcy5tYXAoZz0+Jzx0cj4nK1tnLmphbnBhZCxnLmVuZ2luZWVyKycgLyAnK2cuc2VjdG9yXS5tYXAodj0+Jzx0ZCBzdHlsZT0iZm9udC13ZWlnaHQ6ODAwIj4nK2VzYyh2KSsnPC90ZD4nKS5qb2luKCcnKStjZWxscyhnKSsnPC90cj4nKS5qb2luKCcnKTsKIGNvbnN0IHN1YnRvdGFsPXt0b3RhbDplbnRyaWVzLnJlZHVjZSgocyxnKT0+cytnLnRvdGFsLDApLG9uZ29pbmc6ZW50cmllcy5yZWR1Y2UoKHMsZyk9PnMrZy5vbmdvaW5nLDApLGlzc3VlZFRvdGFsOmVudHJpZXMucmVkdWNlKChzLGcpPT5zK2cuaXNzdWVkVG90YWwsMCksaXNzdWVkTWlzc2luZzplbnRyaWVzLnNvbWUoZz0+Zy5pc3N1ZWRNaXNzaW5nKSx3b3JraW5nR1A6ZW50cmllcy5yZWR1Y2UoKHMsZyk9PnMrZy53b3JraW5nR1AsMCksY291bnRzOmJhbmRzLm1hcCgoYixpKT0+ZW50cmllcy5yZWR1Y2UoKHMsZyk9PnMrZy5jb3VudHNbaV0sMCkpLG1pc3Npbmc6ZW50cmllcy5yZWR1Y2UoKHMsZyk9PnMrZy5taXNzaW5nLDApLG9uZ29pbmdDb3VudHM6d29ya1R5cGVzLm1hcCgodCxpKT0+ZW50cmllcy5yZWR1Y2UoKHMsZyk9PnMrZy5vbmdvaW5nQ291bnRzW2ldLDApKSx3b3JrQ291bnRzOndvcmtUeXBlcy5tYXAoKHQsaSk9PmVudHJpZXMucmVkdWNlKChzLGcpPT5zK2cud29ya0NvdW50c1tpXSwwKSksd29ya01pc3Npbmc6d29ya1R5cGVzLm1hcCgodCxpKT0+ZW50cmllcy5zb21lKGc9Pmcud29ya01pc3NpbmdbaV0pKX07CiB0YWJsZSs9Jzx0ciBzdHlsZT0iYmFja2dyb3VuZDojZGJlYWZlO2ZvbnQtd2VpZ2h0OjgwMCI+PHRkIGNvbHNwYW49IjIiPicrZXNjKGphbnBhZCkrJyDigJQg4KSc4KSo4KSq4KSmIOCkleClgeCksjwvdGQ+JytjZWxscyhzdWJ0b3RhbCkrJzwvdHI+JzsKIH0KIGlmKCFzdW1tYXJ5Lmxlbmd0aCl0YWJsZSs9Jzx0cj48dGQgY29sc3Bhbj0iJytoZWFkZXJzLmxlbmd0aCsnIj7gpJrgpK/gpKgg4KSV4KWHIOCksuCkv+CkjyDgpJfgpY3gpLDgpL7gpK4g4KSq4KSC4KSa4KS+4KSv4KSkIOCkoeClh+Ckn+CkviDgpIngpKrgpLLgpKzgpY3gpKcg4KSo4KS54KWA4KSCIOCkueCliOClpDwvdGQ+PC90cj4nOwoKIGNvbnN0IGdyYW5kPXt0b3RhbDpzdW1tYXJ5LnJlZHVjZSgocyxnKT0+cytnLnRvdGFsLDApLHdvcmtpbmdHUDpzdW1tYXJ5LnJlZHVjZSgocyxnKT0+cytnLndvcmtpbmdHUCwwKSxvbmdvaW5nOnN1bW1hcnkucmVkdWNlKChzLGcpPT5zK2cub25nb2luZywwKSxpc3N1ZWRUb3RhbDpzdW1tYXJ5LnJlZHVjZSgocyxnKT0+cytnLmlzc3VlZFRvdGFsLDApLGlzc3VlZE1pc3Npbmc6c3VtbWFyeS5zb21lKGc9PmcuaXNzdWVkTWlzc2luZyksY291bnRzOmJhbmRzLm1hcCgoYixpKT0+c3VtbWFyeS5yZWR1Y2UoKHMsZyk9PnMrZy5jb3VudHNbaV0sMCkpLG1pc3Npbmc6c3VtbWFyeS5yZWR1Y2UoKHMsZyk9PnMrZy5taXNzaW5nLDApLG9uZ29pbmdDb3VudHM6d29ya1R5cGVzLm1hcCgodCxpKT0+c3VtbWFyeS5yZWR1Y2UoKHMsZyk9PnMrZy5vbmdvaW5nQ291bnRzW2ldLDApKSx3b3JrQ291bnRzOndvcmtUeXBlcy5tYXAoKHQsaSk9PnN1bW1hcnkucmVkdWNlKChzLGcpPT5zK2cud29ya0NvdW50c1tpXSwwKSksd29ya01pc3Npbmc6d29ya1R5cGVzLm1hcCgodCxpKT0+c3VtbWFyeS5zb21lKGc9Pmcud29ya01pc3NpbmdbaV0pKX07CiB0YWJsZSs9Jzx0ciBzdHlsZT0iYmFja2dyb3VuZDojZTVmMGZhO2ZvbnQtd2VpZ2h0OjgwMCI+PHRkIGNvbHNwYW49IjIiPuCkleClgeCksjwvdGQ+JytjZWxscyhncmFuZCkrJzwvdHI+PC90Ym9keT48L3RhYmxlPic7CiBjb25zdCB3b3JrVGFibGU9Jyc7CiBjb25zdCBub3RlPScqID0g4KSJ4KSq4KSy4KSs4KWN4KSnIEdQIOCkuOClhyDgpLjgpKTgpY3gpK/gpL7gpKrgpL/gpKQgTVIg4KSc4KS+4KSw4KWAIOCkleCkvuCksOCljeCkr+Cli+CkgiDgpJXgpL4g4KSc4KWL4KSh4KS8OyDgpJXgpYHgpJsgR1Ag4KSV4KS+IOCkteCkv+CkteCksOCkoyDgpLLgpILgpKzgpL/gpKQg4KS54KWL4KSo4KWHIOCkuOClhyDgpKrgpYLgpLDgpY3gpKMg4KS44KSC4KSW4KWN4KSv4KS+IOCkheCkp+Ckv+CklSDgpLngpYsg4KS44KSV4KSk4KWAIOCkueCliOClpCDgpLLgpL7gpLI6IOCkquCljeCksOCkl+CkpOCkv+CksOCkpCDgpJXgpL7gpLDgpY3gpK8g4KS54KWI4KSCLCBNUiDgpJzgpL7gpLDgpYAg4KSo4KS54KWA4KSCIOKAoiDgpKjgpL7gpLDgpILgpJfgpYA6IOCkleClgeCkmyDgpKrgpY3gpLDgpJfgpKTgpL/gpLDgpKQg4KSV4KS+4KSw4KWN4KSv4KWL4KSCIOCkruClh+CkgiBNUiDgpJzgpL7gpLDgpYAg4KSo4KS54KWA4KSCIOKAoiDgpJXgpL7gpLDgpY3gpK8t4KSq4KWN4KSw4KSV4KS+4KSwIOCkleClhyDgpKrgpY3gpLDgpKTgpY3gpK/gpYfgpJUg4KSV4KWJ4KSy4KSuIOCkruClh+Ckgjog4KSu4KS44KWN4KSf4KSwIOCksOCli+CksiDgpJzgpL7gpLDgpYAg4KSV4KS+4KSw4KWN4KSv4KWL4KSCIOCkleClgCDgpJXgpYHgpLIg4KS44KSC4KSW4KWN4KSv4KS+IC8g4KSV4KWB4KSyIOCkquCljeCksOCkl+CkpOCkv+CksOCkpCDgpJXgpL7gpLDgpY3gpK8g4oCiIOCknOCkqOCkquCkpiwg4KSJ4KSq4KSv4KSC4KSk4KWN4KSw4KWAIOCkj+CkteCkgiDgpJXgpY3gpLLgpLjgpY3gpJ/gpLAg4KSV4KWHIOCkiuCkquCksCDgpKbgpL/gpI8g4KSr4KS84KS/4KSy4KWN4KSf4KSwIOCksuCkvuCkl+ClgiDgpLngpYjgpILgpaQnOwogYm94LmlubmVySFRNTD0nPHN0eWxlPi5tci1ub25le2Rpc3BsYXk6YmxvY2s7YmFja2dyb3VuZDojZmVlMmUyO2NvbG9yOiNiOTFjMWM7Zm9udC13ZWlnaHQ6OTAwO3BhZGRpbmc6M3B4O2JvcmRlcjoxcHggc29saWQgI2VmNDQ0NDtib3JkZXItcmFkaXVzOjNweH0ubXItZ2Fwe2Rpc3BsYXk6YmxvY2s7YmFja2dyb3VuZDojZmZmN2VkO2NvbG9yOiM5YTM0MTI7Zm9udC13ZWlnaHQ6ODAwO3BhZGRpbmc6M3B4fS5tci1va3tjb2xvcjojMTU4MDNkO2ZvbnQtd2VpZ2h0OjgwMH0jZ3BMYWJvdXJNdXN0ZXJNb2R1bGUgdGFibGV7Zm9udC1zaXplOjEzcHg7dGFibGUtbGF5b3V0OmF1dG99I2dwTGFib3VyTXVzdGVyTW9kdWxlIHRoe3doaXRlLXNwYWNlOm5vcm1hbCFpbXBvcnRhbnQ7b3ZlcmZsb3ctd3JhcDpicmVhay13b3JkO21pbi13aWR0aDowO21heC13aWR0aDpub25lO2xpbmUtaGVpZ2h0OjEuM30jZ3BMYWJvdXJNdXN0ZXJNb2R1bGUgdGgsI2dwTGFib3VyTXVzdGVyTW9kdWxlIHRke2JvcmRlcjoxcHggc29saWQgIzc4OTRhYztwYWRkaW5nOjNweH0jZ3BMYWJvdXJNdXN0ZXJNb2R1bGUgdGFibGU6Zmlyc3Qtb2YtdHlwZSB0aDpudGgtY2hpbGQoMyksI2dwTGFib3VyTXVzdGVyTW9kdWxlIHRhYmxlOmZpcnN0LW9mLXR5cGUgdGQ6bnRoLWNoaWxkKDMpe3dpZHRoOjYwcHghaW1wb3J0YW50O21pbi13aWR0aDo2MHB4IWltcG9ydGFudDttYXgtd2lkdGg6NjBweCFpbXBvcnRhbnQ7d2hpdGUtc3BhY2U6bm9ybWFsIWltcG9ydGFudDtvdmVyZmxvdy13cmFwOmFueXdoZXJlO3BhZGRpbmc6M3B4IWltcG9ydGFudDt0ZXh0LWFsaWduOmNlbnRlcjtmb250LXNpemU6MTRweDtsaW5lLWhlaWdodDoxLjN9I2dwTGFib3VyTXVzdGVyTW9kdWxlIHRoOm50aC1jaGlsZCgyKSwjZ3BMYWJvdXJNdXN0ZXJNb2R1bGUgdGQ6bnRoLWNoaWxkKDIpe3doaXRlLXNwYWNlOm5vd3JhcDttaW4td2lkdGg6MDt0ZXh0LWFsaWduOmxlZnR9I2dwTGFib3VyTXVzdGVyTW9kdWxlIHRoe2JhY2tncm91bmQ6IzE0NTg4Yztjb2xvcjp3aGl0ZX0jZ3BMYWJvdXJNdXN0ZXJNb2R1bGUgdGJvZHkgdHI6bnRoLWNoaWxkKGV2ZW4pe2JhY2tncm91bmQ6I2YwZjZmYn1AbWVkaWEgcHJpbnR7I2dwTGFib3VyTXVzdGVyTW9kdWxle2Rpc3BsYXk6bm9uZX19PC9zdHlsZT48aDIgc3R5bGU9Im1hcmdpbjowIDAgOHB4Ij4nK3RpdGxlKyc8L2gyPjxwIHN0eWxlPSJ0ZXh0LWFsaWduOnJpZ2h0O2ZvbnQtd2VpZ2h0OjgwMDttYXJnaW46NHB4IDAgMTBweCI+PHN0cm9uZz7gpKbgpL/gpKjgpL7gpILgpJU6ICcrZXNjKGRhdGUpKyc8L3N0cm9uZz48L3A+PHA+Jytlc2Mobm90ZSkrJzwvcD48cCBzdHlsZT0iY29sb3I6IzlhMzQxMiI+4KSX4KWN4KSw4KS+4KSuIOCkquCkguCkmuCkvuCkr+CkpCDgpJXgpYcg4KSJ4KSq4KSy4KSs4KWN4KSnIOCkuOCljeCksOCli+CkpCDgpIbgpIHgpJXgpKHgpLzgpYcg4KSm4KS/4KSW4KS+4KSPIOCkl+CkjyDgpLngpYjgpII7IOCknOCkqOCkquCkpiDgpJXgpYcg4KSF4KSm4KWN4KSv4KSk4KSoIOCkleClgeCksiDgpLjgpYcg4KSH4KSo4KSV4KS+IOCkheCkguCkpOCksCDgpLngpYsg4KS44KSV4KSk4KS+IOCkueCliOClpCDgpJXgpYngpLLgpK4gNiDgpLjgpYcg4KSq4KWN4KSw4KS+4KSq4KWN4KSkIE1SIOCknOCkvuCksOClgCDgpLXgpL7gpLLgpYcg4KSV4KS+4KSw4KWN4KSv4KWL4KSCIOCkleClgCDgpJXgpL7gpLDgpY3gpK8g4KSq4KWN4KSw4KSV4KS+4KSw4KS14KS+4KSwIOCkuOCkguCkluCljeCkr+CkviDgpKbgpL/gpJbgpL7gpIgg4KSc4KS+4KSP4KSX4KWA4KWkIOCkuOCkpOCljeCkr+CkvuCkquCkv+CkpCDgpJXgpL7gpLDgpY3gpK8g4KS44KWC4KSa4KWAIOCkieCkquCksuCkrOCljeCkpyDgpKgg4KS54KWL4KSo4KWHIOCkquCksCDigJQg4KSm4KS/4KSW4KS+4KSv4KS+IOCkl+Ckr+CkviDgpLngpYjgpaQgQ0MgUm9hZCDgpJTgpLAgR3JhdmVsIFJvYWQsIFJ1cmFsIENvbm5lY3Rpdml0eSDgpJXgpYcg4KSF4KSC4KSk4KSw4KWN4KSX4KSkIOCkueCliOCkguClpDwvcD48YnV0dG9uIHR5cGU9ImJ1dHRvbiIgaWQ9ImdwTGFib3VyTXVzdGVyUHJpbnQiIHN0eWxlPSJwYWRkaW5nOjlweCAxNXB4O2JhY2tncm91bmQ6IzE0NTg4Yztjb2xvcjp3aGl0ZTtib3JkZXI6MDtib3JkZXItcmFkaXVzOjdweDtmb250LXdlaWdodDo4MDAiPuCkh+CkuCDgpK7gpYngpKHgpY3gpK/gpYLgpLIg4KSV4KS+IOCkquCljeCksOCkv+CkguCknyAvIFBERjwvYnV0dG9uPjxkaXYgc3R5bGU9Im92ZXJmbG93OmF1dG87bWFyZ2luLXRvcDoxMnB4Ij4nK3RhYmxlK3dvcmtUYWJsZSsnPC9kaXY+JzsKIGRvY3VtZW50LmdldEVsZW1lbnRCeUlkKCdncExhYm91ck11c3RlclByaW50Jykub25jbGljaz0oKT0+ewogY29uc3Qgdz13aW5kb3cub3BlbignJywnX2JsYW5rJyk7aWYoIXcpe2FsZXJ0KCfgpKrgpY3gpLDgpL/gpILgpJ8g4KSV4KWHIOCksuCkv+CkjyBwb3B1cCDgpIXgpKjgpYHgpK7gpKTgpL8g4KSm4KWH4KSC4KWkJyk7cmV0dXJuO30KIHcuZG9jdW1lbnQud3JpdGUoJzwhZG9jdHlwZSBodG1sPjxodG1sIGxhbmc9ImhpIj48aGVhZD48bWV0YSBjaGFyc2V0PSJ1dGYtOCI+PHRpdGxlPicrdGl0bGUrJzwvdGl0bGU+PHN0eWxlPi5tci1ub25le2Rpc3BsYXk6YmxvY2s7YmFja2dyb3VuZDojZmVlMmUyO2NvbG9yOiNiOTFjMWM7Zm9udC13ZWlnaHQ6OTAwO3BhZGRpbmc6M3B4O2JvcmRlcjoxcHggc29saWQgI2VmNDQ0NDtib3JkZXItcmFkaXVzOjNweH0ubXItZ2Fwe2Rpc3BsYXk6YmxvY2s7YmFja2dyb3VuZDojZmZmN2VkO2NvbG9yOiM5YTM0MTI7Zm9udC13ZWlnaHQ6ODAwO3BhZGRpbmc6M3B4fS5tci1va3tjb2xvcjojMTU4MDNkO2ZvbnQtd2VpZ2h0OjgwMH1AcGFnZXtzaXplOkE0IGxhbmRzY2FwZTttYXJnaW46OG1tfWJvZHl7Zm9udC1mYW1pbHk6QXJpYWwsc2Fucy1zZXJpZjtjb2xvcjojMTExfXRhYmxle3dpZHRoOjEwMCUhaW1wb3J0YW50O3RhYmxlLWxheW91dDpmaXhlZCFpbXBvcnRhbnQ7Ym9yZGVyLWNvbGxhcHNlOmNvbGxhcHNlO2ZvbnQtc2l6ZTo5cHh9Y29se3dpZHRoOmF1dG8haW1wb3J0YW50fXRoLHRke2JvcmRlcjoxcHggc29saWQgIzMzMztwYWRkaW5nOjRweH10aHtiYWNrZ3JvdW5kOiNlNWYwZmF9dGFibGU6Zmlyc3Qtb2YtdHlwZSB0aDpudGgtY2hpbGQoMyksdGFibGU6Zmlyc3Qtb2YtdHlwZSB0ZDpudGgtY2hpbGQoMyl7d2lkdGg6OW1tO21heC13aWR0aDo5bW07cGFkZGluZzoycHg7d2hpdGUtc3BhY2U6bm9ybWFsfXRoOm50aC1jaGlsZCgyKSx0ZDpudGgtY2hpbGQoMil7d2hpdGUtc3BhY2U6bm93cmFwO3RleHQtYWxpZ246bGVmdDt3aWR0aDoxJX10aGVhZHtkaXNwbGF5OnRhYmxlLWhlYWRlci1ncm91cH10cnticmVhay1pbnNpZGU6YXZvaWR9aDJ7Zm9udC1zaXplOjE4cHh9PC9zdHlsZT48L2hlYWQ+PGJvZHk+PGgyPicrdGl0bGUrJzwvaDI+PHAgc3R5bGU9InRleHQtYWxpZ246cmlnaHQ7Zm9udC13ZWlnaHQ6ODAwO21hcmdpbjo0cHggMCAxMHB4Ij48c3Ryb25nPuCkpuCkv+CkqOCkvuCkguCklTogJytlc2MoZGF0ZSkrJzwvc3Ryb25nPjwvcD48cD4nK2VzYyhub3RlKSsnPC9wPicrdGFibGUrd29ya1RhYmxlKyc8L2JvZHk+PC9odG1sPicpOwogdy5vbmxvYWQ9KCk9PncucHJpbnQoKTt3LmRvY3VtZW50LmNsb3NlKCk7fTsKfQpjb25zdCBvbGQ9cmVuZGVyO3JlbmRlcj1mdW5jdGlvbigpe2NvbnN0IHJlc3VsdD1vbGQuYXBwbHkodGhpcyxhcmd1bWVudHMpO2RyYXcoKTtyZXR1cm4gcmVzdWx0O307ZHJhdygpOwoKLy8gTG9hZCB0aGUgdmVyaWZpZWQgZGF0YSBpbmRlcGVuZGVudGx5OiB0aGUgbGVnYWN5IHBhZ2UgbG9hZGVyIHNpdHMgaW5zaWRlIHByaW50IEhUTUwuCmZldGNoKCdncC1lbXVzdGVyLWRhdGEuanM/bGl2ZT0nK0RhdGUubm93KCkse2NhY2hlOiduby1zdG9yZSd9KQogLnRoZW4ocj0+e2lmKCFyLm9rKXRocm93IG5ldyBFcnJvcignR1AgZGF0YSBIVFRQICcrci5zdGF0dXMpO3JldHVybiByLnRleHQoKTt9KQogLnRoZW4odGV4dD0+ewogIGNvbnN0IG1hdGNoPXRleHQubWF0Y2goL15ccyp3aW5kb3dcLkdQX1dPUktfVFlQRV9NVVNURVJfUkVQT1JUXHMqPVxzKihbXHNcU10qPylccyo7P1xzKiQvKTsKICBpZighbWF0Y2gpdGhyb3cgbmV3IEVycm9yKCdVbmV4cGVjdGVkIEdQIGRhdGEgZm9ybWF0Jyk7CiAgY29uc3QgcGFyc2VkPUpTT04ucGFyc2UobWF0Y2hbMV0pOwogIGlmKCFBcnJheS5pc0FycmF5KHBhcnNlZC5yb3dzKXx8cGFyc2VkLnJvd3MubGVuZ3RoIT09Njk1fHwhQXJyYXkuaXNBcnJheShwYXJzZWQud29ya3MpKXRocm93IG5ldyBFcnJvcignSW5jb21wbGV0ZSBHUCBkYXRhJyk7CiAgd2luZG93LkdQX1dPUktfVFlQRV9NVVNURVJfUkVQT1JUPXBhcnNlZDsKICBkcmF3KCk7CiB9KS5jYXRjaChlcnJvcj0+e2NvbnNvbGUuZXJyb3IoJ0dQIHJlcG9ydCBsb2FkIGZhaWxlZCcsZXJyb3IpO2lmKGJveCl7Y29uc3QgcD1kb2N1bWVudC5jcmVhdGVFbGVtZW50KCdwJyk7cC5zdHlsZS5jb2xvcj0nI2I5MWMxYyc7cC50ZXh0Q29udGVudD0n4KSV4KS+4KSw4KWN4KSvIOCkquCljeCksOCkleCkvuCksCDgpKHgpYfgpJ/gpL4g4KSy4KWL4KShIOCkqOCkueClgOCkgiDgpLngpYHgpIY6ICcrZXJyb3IubWVzc2FnZTtib3gucHJlcGVuZChwKTt9fSk7Cgp9KSgpOw==
# SRDM_EMBEDDED_UPDATER
"""Laptop Chrome: official block -> GP -> column 6 -> work list. Fail closed."""
import argparse, json, re, sys, os
from pathlib import Path
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
TYPES = ['PMAY-G','CC Road','Gravel Road','Play Ground','Khet Talab','Dug Pond','Old Water Bodies','Water Structure','Ek Bagiya','Other Plantation','Other Works']
BLOCKS = {'AMARPATAN','MAIHAR','MAJHGAWAN','NAGOD','RAMNAGAR','RAMPUR BAGHELAN','SATNA','UNCHAHARA'}
GRID = """()=>Array.from(document.querySelectorAll('table')).map(t=>{const g=[];Array.from(t.rows).filter(r=>r.closest('table')===t).forEach((r,y)=>{g[y]??=[];let x=0;Array.from(r.cells).forEach(c=>{while(g[y][x]!==undefined)x++;const v={text:c.innerText.trim(),links:Array.from(c.querySelectorAll('a[href]')).map(a=>a.href)};for(let dy=0;dy<c.rowSpan;dy++){g[y+dy]??=[];for(let dx=0;dx<c.colSpan;dx++)g[y+dy][x+dx]=v}x+=c.colSpan})});return g})"""

def clean(v): return re.sub(r'\s+', ' ', str(v or '')).strip()
def key(v): return re.sub(r'[^A-Z0-9\u0900-\u097f]', '', clean(v).upper())
def block(v):
    v=clean(v).upper()
    return {'SOHAWAL':'SATNA','RAMPURBAGHELAN':'RAMPUR BAGHELAN'}.get(v,v)
def count(v):
    s=clean(v).replace(',','')
    if not re.fullmatch(r'\d+',s): raise ValueError('Invalid official count: '+s)
    return int(s)
def read_js(path):
    s=path.read_text(encoding='utf-8-sig');return json.loads(s.split('=',1)[1].strip().rstrip(';'))
def classify(name, kind):
    n=clean(name).lower(); t=(n+' '+clean(kind).lower())
    if re.search(r'pmay|pradhan.*awas|प्रधान.*आवास',t):return 'PMAY-G'
    if re.search(r'^(?:ek\s+)?bagiya\b|^एक\s+बगिया|^(?:एक\s+)?माँ.*बगिया|^ek\s+ma+a?\s+ke\s+naam',n):return 'Ek Bagiya'
    if re.search(r'khet\s*talab|farm\s*pond|खेत\s*तालाब',t):return 'Khet Talab'
    if re.search(r'dug\s*pond|डग\s*पोंड|डुग\s*पोंड',t):return 'Dug Pond'
    if re.search(r'old\s*water|renovation.*(?:water\s*bod|traditional\s*water)|पुरान.*(?:तालाब|जल)',t):return 'Old Water Bodies'
    if re.search(r'play\s*(?:ground|field)|खेल.*मैदान',t):return 'Play Ground'
    if re.search(r'gravel|grewal|greval|graval|ग्रेवल|ग्रेवल|मुरुम|mur+am',t):return 'Gravel Road'
    if re.search(r'(?:\bcc\b|cement\s*concrete|सीसी|सी\.सी).*?(?:road|सड़क)|(?:road|सड़क).*?(?:\bcc\b|cement\s*concrete)',t):return 'CC Road'
    if re.search(r'stop\s*dam|check\s*dam|water\s*(?:structure|conserv|harvest)|recharge|percolation|जल.*(?:संरक्षण|संचय)|स्टाप|चेक.*डैम',t):return 'Water Structure'
    if re.search(r'plantation|horticulture|afforestation|वृक्षारोपण|पौधरोपण|चारागाह|बगिया',t):return 'Other Plantation'
    return 'Other Works'

def blocks_from(tables):
    found={}
    for table in tables:
        for row in table:
            if len(row)<6:continue
            b=block(row[1]['text'])
            if b not in BLOCKS:continue
            try:gp,labour,works=count(row[2]['text']),count(row[4]['text']),count(row[5]['text'])
            except ValueError:continue
            item={'janpad':b,'gps':gp,'labour':labour,'works':works,'links':row[1]['links'],'workLinks':row[5]['links']}
            if b in found and found[b]!=item:raise ValueError('Ambiguous block rows: '+b)
            found[b]=item
    if set(found)!=BLOCKS:raise ValueError('Expected 8 Janpad hyperlinks; found '+str(list(found)))
    if sum(r['gps'] for r in found.values())!=695:raise ValueError('Expected 695 GPs in source')
    return found

def header_col(names, pattern):
    indices=[i for i,n in enumerate(names) if re.search(pattern,n,re.I)]
    return indices[0] if len(indices)==1 else None
def gps_from(tables, expected):
    candidates=[]
    for table in tables:
        for hi,row in enumerate(table):
            names=[clean(c['text']) for c in row]
            gi=header_col(names,r'^(?:gram\s*)?panchayat(?:s|\s*name)?$|^GP\s*name$')
            li=header_col(names,r'expected.*labour|labour.*engagement')
            wi=header_col(names,r'ongoing\s*works.*muster|works.*MR.*issued')
            mi=header_col(names,r'^No\.?\s*of\s*Muster\s*Rolls|^Muster\s*Rolls\s*\(MRs\)')
            if None in (gi,li,wi):continue
            out={}
            for r in table[hi+1:]:
                if len(r)<=max(gi,li,wi) or re.search(r'\btotal\b',r[gi]['text'],re.I):continue
                try:labour,works=count(r[li]['text']),count(r[wi]['text'])
                except ValueError:continue
                gp=clean(r[gi]['text'])
                if not gp or gp.isdigit():continue
                gk=key(gp)
                if gk in out:raise ValueError('Duplicate GP: '+gp)
                out[gk]={'panchayat':gp,'labour':labour,'worksMR':works,'mrs':count(r[mi]['text']) if mi is not None else None,'workLinks':r[wi]['links'],'labourLinks':r[li]['links']}
            if len(out)==expected['gps'] and sum(g['labour'] for g in out.values())==expected['labour'] and sum(g['worksMR'] for g in out.values())==expected['works']:candidates.append(list(out.values()))
    if not candidates:raise ValueError('GP table missing/incomplete or GP/labour/work totals do not match '+expected['janpad'])
    return candidates[0]

def works_from(tables, expected, gp=None, partial=False):
    candidates=[]
    for table in tables:
        for hi,row in enumerate(table):
            names=[re.sub(r'\s*\(?\d+\)?\s*$', '', clean(c['text'])) for c in row]
            ci=header_col(names,r'work\s*(?:code|id|number|no\.?)')
            ni=header_col(names,r'work\s*name|name\s*of\s*(?:the\s*)?work')
            # Source has both Work Category and Work Type. Prefer the detailed type.
            ti=header_col(names,r'^(?:type\s*of\s*work|work\s*type)$')
            if ti is None:
                ti=header_col(names,r'^(?:permissible\s*work|work\s*category|category\s*of\s*work)$')
            li=header_col(names,r'expected.*labour|labour.*engagement|^(?:no\.?\s*of\s*)?(?:workers|labour|labourers)$')
            if ni is None or ti is None:continue
            out={}
            for r in table[hi+1:]:
                if len(r)<=max(ni,ti,ci if ci is not None else 0):continue
                name=clean(r[ni]['text']);kind=clean(r[ti]['text'])
                raw=clean(r[ci]['text']) if ci is not None else clean(r[ni]['text'])
                matches=re.findall(r'(?<![0-9])\d{5,}/[A-Za-z0-9]+/\d+(?![0-9])',raw)
                if not matches:
                    from urllib.parse import unquote
                    links=' '.join(unquote(u) for c in r for u in c.get('links',[]))
                    matches=re.findall(r'(?<![0-9])\d{5,}/[A-Za-z0-9]+/\d+(?![0-9])',links)
                codes=set(matches)
                work_code=next(iter(codes)) if len(codes)==1 else raw if ci is not None else ''
                if not re.search(r'\d{5,}',work_code) or not name or not kind:continue
                code=work_code
                item={'code':code,'name':name,'type':kind,'category':classify(name,kind),'panchayat':gp}
                item['labour']=count(r[li]['text']) if li is not None else None
                if code in out and out[code]!=item:raise ValueError('Conflicting duplicate work code '+code)
                out[code]=item
            if len(out)==expected or (partial and out):candidates.append(list(out.values()))
    if not candidates:raise ValueError('Work detail incomplete: expected '+str(expected)+' unique codes; pagination/export may be required')
    if partial:return max(candidates,key=len)
    return candidates[0]

NEXT_PAGE = r'''()=>Array.from(document.querySelectorAll('a,button,input[type=submit],input[type=button]')).filter(e=>{
 const text=(e.innerText||e.value||e.getAttribute('aria-label')||e.title||'').trim();
 return /^(?:next(?:\s*(?:page|[>»]))?|[>»›]|अगला)$/i.test(text) && !e.disabled && e.getAttribute('aria-disabled')!=='true' && e.getClientRects().length;
}).map(e=>({text:(e.innerText||e.value||e.getAttribute('aria-label')||e.title||'').trim(),href:e.getAttribute('href')}))'''

def collect_work_pages(page,tables,expected,gp):
    found={};seen=set()
    for page_no in range(1,501):
        fingerprint=json.dumps(tables,ensure_ascii=False,sort_keys=True)
        if fingerprint in seen:raise ValueError('Work pagination repeated page '+str(page_no))
        seen.add(fingerprint)
        for item in works_from(tables,expected,gp,partial=True):
            previous=found.get(item['code'])
            if previous is not None and previous!=item:raise ValueError('Conflicting paginated work '+item['code'])
            found[item['code']]=item
        if len(found)==expected:return list(found.values())
        if len(found)>expected:raise ValueError('Work detail exceeds official count')
        next_controls=page.evaluate(NEXT_PAGE)
        if len(next_controls)!=1:raise ValueError('Work detail incomplete: expected '+str(expected)+' unique codes, found '+str(len(found))+'; no unambiguous next page')
        selected=next_controls[0]
        controls=page.locator('a,button,input[type=submit],input[type=button]')
        clicked=False
        for i in range(controls.count()):
            control=controls.nth(i)
            label=control.evaluate("e=>(e.innerText||e.value||e.getAttribute('aria-label')||e.title||'').trim()")
            if label==selected['text'] and control.is_visible() and control.is_enabled():
                control.click(timeout=30000);clicked=True;break
        if not clicked:raise ValueError('Next page could not be opened')
        page.wait_for_function('(old)=>JSON.stringify(('+GRID+')())!==old',arg=json.dumps(tables,ensure_ascii=False,separators=(',',':')),timeout=30000)
        tables=page.evaluate(GRID)
    raise ValueError('Work pagination limit reached')


def resolve_by_labour(fetch, tables, gp):
    candidates=works_from(tables,gp['worksMR'],gp['panchayat'],partial=True)
    bycode={w['code']:w for w in candidates}
    errors=[]
    for url in gp.get('labourLinks',[]):
        try:
            labour_tables=fetch(url)
            codes=set()
            for table in labour_tables:
                for row in table:
                    for cell in row:
                        codes.update(re.findall(r'(?<![0-9])\d{5,}/(?:[A-Za-z0-9]+/)+\d+(?![0-9])',cell['text']))
            if len(codes)!=gp['worksMR'] or not codes.issubset(bycode):
                raise ValueError('Labour work codes do not uniquely resolve MR works: '+str(len(codes)))
            return [bycode[c] for c in sorted(codes)]
        except Exception as e:errors.append(str(e))
    raise ValueError('Work list conflicts with GP total; labour-code verification failed: '+'; '.join(errors))

def main():
    a=argparse.ArgumentParser();a.add_argument('--url',required=True);a.add_argument('--headed',action='store_true');a.add_argument('--repair-missing',action='store_true');args=a.parse_args()
    from playwright.sync_api import sync_playwright
    master=read_js(ROOT/'auto-data.js')['rows']
    ongoing=read_js(ROOT/'ongoing-details.js')
    categories={clean(r['code']):r.get('finalCategory') or 'Other Works' for r in ongoing}
    work_categories=sorted(set(categories.values()))
    sys.path.insert(0,str(ROOT/'scripts'))
    import ast
    category_source=ROOT/'scripts'/'update_daily_report.py'
    tree=ast.parse(category_source.read_text(encoding='utf-8-sig'))
    functions=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name in ('c','final_category')]
    namespace={'re':re}
    exec(compile(ast.Module(body=functions,type_ignores=[]),str(category_source),'exec'),namespace)
    final_category=namespace['final_category']
    mapping={(block(r['janpad']),key(r['panchayat'])):r for r in master}
    debug=ROOT/'data'/'gp-emuster-debug';debug.mkdir(parents=True,exist_ok=True)
    def dump(name,value):(debug/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False),encoding='utf-8')
    output=[];all_works=[]
    previous=read_js(ROOT/'gp-emuster-data.js') if args.repair_missing and (ROOT/'gp-emuster-data.js').exists() else {}
    previous_rows={(block(r['janpad']),key(r['panchayat'])):r for r in previous.get('rows',[])}
    previous_works={}
    for w in previous.get('works',[]):previous_works.setdefault((block(w['janpad']),key(w['panchayat'])),[]).append(w)

    with sync_playwright() as p:
        try:browser=p.chromium.launch(channel='chrome',headless=not args.headed)
        except Exception:browser=p.chromium.launch(headless=not args.headed)
        ctx=browser.new_context();page=ctx.new_page()
        def fetch(url):
            if urlparse(url).hostname!='vbgramgrep.dord.gov.in':raise ValueError('Unexpected source host')
            response=page.goto(url,wait_until='domcontentloaded',timeout=90000)
            if response and response.status>=400:raise ValueError('Official HTTP '+str(response.status))
            page.locator('table').first.wait_for(timeout=30000)
            return page.evaluate(GRID)
        try:
            top=fetch(args.url);dump('main',top);blocks=blocks_from(top)
            date_match=re.search(r'(?:report\s*)?last\s*updated(?:\s*on)?\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})',page.locator('body').inner_text(),re.I)
            source_date=date_match.group(1).replace('/','-') if date_match else 'तिथि उपलब्ध नहीं'
            today=datetime.now(timezone(timedelta(hours=5,minutes=30))).strftime('%d-%m-%Y')
            if source_date != today:print('NOTE: Source Last Updated '+source_date+'; validating against current 8-Janpad totals before accepting this snapshot.',flush=True)
            import csv
            with (ROOT/'data'/'official-summary.csv').open(encoding='utf-8-sig',newline='') as handle:
                official={block(r['janpad']):r for r in csv.DictReader(handle)}
            for b,summary in blocks.items():
                o=official.get(b)
                if not o or any(int(float(o[k]))!=summary[v] for k,v in [('totalGP','gps'),('labourAll','labour'),('mrAll','works')]):
                    raise ValueError('GP source differs from current Janpad summary: '+b)
            for b,summary in blocks.items():
                print('Janpad: '+b,flush=True)
                errors=[];gps=None
                for url in summary['links']:
                    try:
                        tables=fetch(url);dump(b+'-gp',tables);gps=gps_from(tables,summary);break
                    except Exception as e:errors.append(str(e))
                if gps is None:raise ValueError(b+' GP fetch failed: '+'; '.join(errors))
                for gp in gps:
                    mk=(b,key(gp['panchayat']))
                    if mk not in mapping:raise ValueError('GP engineer mapping missing: '+str(mk))
                    entry=mapping[mk].copy();entry.update({k:v for k,v in gp.items() if k not in ('workLinks','labourLinks')});entry['janpad']=b
                    old=previous_rows.get(mk);old_works=previous_works.get(mk,[])
                    if (args.repair_missing and previous.get('date')==today and old and old.get('detailVerified') and old.get('issuedWorks') is not None
                        and old.get('worksMR')==gp['worksMR'] and old.get('labour')==gp['labour']
                        and len(old_works)==gp['worksMR'] and sum(old['issuedWorks'].values())==gp['worksMR']):
                        entry['issuedWorks']=old['issuedWorks'];entry['detailVerified']=True
                        output.append(entry);all_works.extend(old_works)
                        print('  '+gp['panchayat']+': current verified details retained',flush=True)
                        continue
                    counts=dict.fromkeys(work_categories,0);works=[]
                    if gp['worksMR']:
                        errors=[];verified=False
                        for url in gp['workLinks']:
                            try:
                                last_error=None
                                for attempt in range(1,4):
                                    try:
                                        tables=fetch(url);dump(b+'-'+key(gp['panchayat'])+'-works',tables)
                                        try:works=works_from(tables,gp['worksMR'],gp['panchayat'])
                                        except ValueError:
                                            try:works=collect_work_pages(page,tables,gp['worksMR'],gp['panchayat'])
                                            except ValueError:works=resolve_by_labour(fetch,tables,gp)
                                        last_error=None;break
                                    except Exception as e:
                                        last_error=e
                                        print('  RETRY '+b+'/'+gp['panchayat']+' '+str(attempt)+'/3: '+str(e),flush=True)
                                        dump(b+'-'+key(gp['panchayat'])+'-failure',{'url':page.url,'error':str(e),'body':page.locator('body').inner_text()})
                                        if attempt<3:page.wait_for_timeout(2000*attempt)
                                if last_error is not None:raise last_error
                                verified=True;break
                            except Exception as e:errors.append(str(e))
                        if not verified:
                            print('DETAIL UNAVAILABLE '+b+'/'+gp['panchayat']+': '+'; '.join(errors),flush=True)
                            counts=None;works=[]
                    for work in works:
                        work['category']=categories.get(work['code']) or final_category(work['name'],work['type'],'2026-2027')
                        counts[work['category']]=counts.get(work['category'],0)+1;work['janpad']=b
                    if counts is not None and works and all(w['labour'] is not None for w in works) and sum(w['labour'] for w in works)!=gp['labour']:
                        print('DETAIL UNAVAILABLE: Work labour differs from GP total: '+b+'/'+gp['panchayat'],flush=True)
                        counts=None;works=[]
                    entry['issuedWorks']=counts;entry['detailVerified']=counts is not None;output.append(entry);all_works.extend(works)
                    print('  '+gp['panchayat']+': '+(str(len(works))+' works verified' if counts is not None else 'GP totals verified; work categories unavailable'),flush=True)
            closing=blocks_from(fetch(args.url))
            for b in blocks:
                if any(closing[b][k]!=blocks[b][k] for k in ('gps','labour','works')):raise ValueError('Source changed during download: '+b+'; rerun update')
        finally:browser.close()
    expected=sum(x['works'] for x in blocks.values())
    if len(output)!=695 or len({(r['janpad'],key(r['panchayat'])) for r in output})!=695:raise ValueError('695 unique GPs required')
    verified_expected=sum(r['worksMR'] for r in output if r['detailVerified'])
    if len(all_works)!=verified_expected or len({w['code'] for w in all_works})!=verified_expected:raise ValueError('Verified work list total/unique codes mismatch')
    payload={'source':args.url,'fetchedAt':datetime.now(timezone.utc).isoformat(),'date':today,'sourceLastUpdated':source_date,'validatedAgainst':'current 8-Janpad summary','totalWorks':expected,'workCategories':sorted(set(work_categories)|{w['category'] for w in all_works}),'rows':output,'works':all_works,'detailsComplete':all(r['detailVerified'] for r in output)}
    missing=[r for r in output if not r['detailVerified']]
    print('DETAIL COMPLETENESS: '+str(len(missing))+' GP pending, '+str(sum(r['worksMR'] for r in missing))+' works pending',flush=True)
    path=ROOT/'gp-emuster-data.js';temp=path.with_suffix('.tmp')
    temp.write_text('window.GP_WORK_TYPE_MUSTER_REPORT = '+json.dumps(payload,ensure_ascii=False)+';\n',encoding='utf-8');os.replace(temp,path)
    print('SUCCESS: 695 GP, '+str(expected)+' MR-issued works; unavailable category details shown as dash. '+str(path),flush=True)

if __name__=='__main__':
    try:main()
    except Exception as e:print('FAILED: '+str(e)+'; previous report preserved.',file=sys.stderr);sys.exit(1)
