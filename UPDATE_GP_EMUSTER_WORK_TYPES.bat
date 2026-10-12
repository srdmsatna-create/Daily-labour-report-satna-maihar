@echo off
setlocal EnableExtensions
title SRDM GP e-Muster Work Type Update
set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar"
if not exist "%REPO%\.git" (
 echo ERROR: Repository not found: %REPO%
 pause
 exit /b 1
)
cd /d "%REPO%"
where py >nul 2>&1
if errorlevel 1 (set "PYTHON_CMD=python") else (set "PYTHON_CMD=py")
if not exist scripts_local mkdir scripts_local
echo Downloading current GP e-Muster updater...
%PYTHON_CMD% -c "import urllib.request,pathlib; u='https://raw.githubusercontent.com/srdmsatna-create/Daily-labour-report-satna-maihar/main/scripts_local/update_gp_emuster.py'; data=urllib.request.urlopen(u,timeout=60).read(); compile(data,u,'exec'); pathlib.Path('scripts_local/update_gp_emuster.py').write_bytes(data)"
if errorlevel 1 goto failed
%PYTHON_CMD% -c "import playwright"
if errorlevel 1 (
 echo Install required dependency once: py -m pip install playwright
 goto failed
)
echo Reading 8 Janpad hyperlinks, GP data and column 6 work lists...
%PYTHON_CMD% scripts_local\update_gp_emuster.py --headed --url "https://vbgramgrep.dord.gov.in/VBGRAMG/dpc_sms_new.aspx?payload=eF3dNGMR7xWiC7cbh_8oTeSuYj9sLPRpM2Qz-IDD_z-ILP-u7C_QNNmuLYIXVz0ap3f0MlYgKjYZXCIhgs6kJ8kuns9vSb9GT5x5eh3KR8ylabbjE4evwn5cuK03ZioNlyPKuge6h8tLqyX5lJeQO8S87NW5IUg4p8vd606CR95HI-WnD2hAbR7CtOm-6o_hsR3_ZJ5dt4USgeXs4gjw-DvDTHlEGf4j80-KWw4f2IVOWIC1RkCLuBsWX-DCzQGGRfRJGerdnJnuB-jHVh6bCjwnjzhBZhJpuXwUzs-vYjdRmOtloSn5XVQ3EqPVODk_TdZBNSbDwldOO20oTo_19L4IhUrxv5My72RX6T8W31w"
if errorlevel 1 goto failed
git fetch origin main
if errorlevel 1 goto failed
set "PUBLISH_DIR=%TEMP%\SRDM_GP_EMUSTER_%RANDOM%_%RANDOM%"
git worktree add --detach "%PUBLISH_DIR%" origin/main
if errorlevel 1 goto failed
copy /y gp-emuster-data.js "%PUBLISH_DIR%\gp-emuster-data.js" >nul
if errorlevel 1 goto failed
git -C "%PUBLISH_DIR%" add -- gp-emuster-data.js
if errorlevel 1 goto failed
git -C "%PUBLISH_DIR%" diff --cached --quiet
if not errorlevel 1 goto unchanged
git -C "%PUBLISH_DIR%" commit -m "Update verified GP labour and issued-MR work type list"
if errorlevel 1 goto failed
git -C "%PUBLISH_DIR%" push origin HEAD:main
if errorlevel 1 goto failed
git worktree remove "%PUBLISH_DIR%"
echo SUCCESS: Verified GP and work-type data published. Refresh site with Ctrl+Shift+R.
pause
exit /b 0
:unchanged
git worktree remove "%PUBLISH_DIR%"
echo SUCCESS: Verified data is already current.
pause
exit /b 0
:failed
echo ERROR: Update incomplete. Previous online data retained. Share the error shown above.
pause
exit /b 1
