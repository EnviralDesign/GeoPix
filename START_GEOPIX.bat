:: turn off echo, so we only print intentional user messages.
@echo off

:: use this to break the script at this point, and not go any further
rem exit /b 1

:: set this for proper variable expansion in for loops.
setlocal enableDelayedExpansion

:: change current working cmd directory to the root where batch executes from.
:: NOTE we might be able to nix this if we expand all our paths to absolute..
cd /d %~dp0

:: wipe and reinit our log, with blank.
break>start_geopix_Log.txt

:: log some things
@echo.
@echo "===================================">>start_geopix_Log.txt
@echo "====== BEGIN GeoPix BootStrap =====">>start_geopix_Log.txt
@echo "===================================">>start_geopix_Log.txt
@echo "==================================="
@echo "====== BEGIN GeoPix BootStrap ====="
@echo "==================================="


:: Define some TD version specific variables. TODO: pull these from files on disk?
SET td_year=2020
SET td_version=28110
SET geopix_executable=GeoPix_2.0.toe

:: Define the absolute path to the wget executable, bundled with GeoPix.
SET wget_executable_path=%~dp0GP\Utilities\wget.exe

:: This directory is where the local copy of TouchDesigner will be installed, if it is not found installed on the system already.
SET td_path_abs=%~dp0.td

:: This directory is a temp one, where certain files will be processed during the batch file execution.
SET tmp_path_abs=%~dp0.tmp

:: This will be the path to the td intaller executable, that the script downloads if no matching TD is found on the system.
SET td_installer_executable_abs="%~dp0.tmp\TouchDesigner.%td_year%.%td_version%.exe"

:: This is the url where we will fetch the TouchDesigner installer from Derivative's website. 
:: It is mostly static, with the year and version subbed in via variables.
SET td_installer_url="https://download.derivative.ca/TouchDesigner.%td_year%.%td_version%.exe"

:: This is the registry value we check to see if the correct version of TouchDesigner is installed already.
SET registry_query_str="HKEY_CLASSES_ROOT\TouchDesigner.%td_year%.%td_version%\shell\open\command"

:: This is the full execution string for downloading the TouchDesigner installer via included wget.
SET td_download_exec_str="%wget_executable_path%" -nv --show-progress -a start_geopix_Log.txt -P "%tmp_path_abs%" "%td_installer_url%"

:: This is the full path to the GeoPix executable, named above via the "geopix_executable" variable.
SET gp_executable_path_abs="%~dp0GP\%geopix_executable%"

:: This is the full path to the GeoPix Fetch Library Assets batch script.
SET library_fetch_script_path_abs="%~dp0FETCH_LIBRARY_ASSETS.bat"

:: This is the full path to the TouchDesigner executable. We init blank, then set later if found in windows registry.
SET td_executable_path=

:: Log some stuff.
@echo "1)--Searching for previously installed version of TouchDesigner.%td_year%.%td_version%----">>start_geopix_Log.txt
@echo "1)--Searching for previously installed version of TouchDesigner.%td_year%.%td_version%----"

:: IF registry entry exists, get path to TD executable and set to variable td_executable_path
:: Next, trim off the last 5 characters to get the pure path. !! characters are used for DelayedExpansion
reg query %registry_query_str% >nul
if %errorlevel% equ 0 (
    FOR /F "usebackq tokens=2,* skip=2" %%L IN (
        `reg query "%registry_query_str%"`
    ) DO SET td_executable_path=%%M
    SET td_executable_path=!td_executable_path:~0,-5!
    if exist !td_executable_path! goto ReadyToLaunch
) else (
    goto InstallTD
)

:InstallTD
:: Log some stuff.
@echo "2)--TouchDesigner.%td_year%.%td_version% not found, installing locally----">>start_geopix_Log.txt
@echo "2)--TouchDesigner.%td_year%.%td_version% not found, installing locally----"

:: If the .tmp directory exists, delete it and recreate.
if exist "%tmp_path_abs%" (
    del /S /Q "%tmp_path_abs%" 
    rmdir /S /Q "%tmp_path_abs%" 
)

:: If the .td directory exists, delete it and recreate.
if exist "%td_path_abs%" (
    del /S /Q "%td_path_abs%" 
    rmdir /S /Q "%td_path_abs%" 
)

:: Log some stuff.
@echo "3)--Succesfully deleted .td and .tmp folders----">>start_geopix_Log.txt
@echo "3)--Succesfully deleted .td and .tmp folders----"

:: recreate the tmp directory.
mkdir "%tmp_path_abs%"


:: Log some stuff.
@echo "4)--Downloading TouchDesigner Installer from Derivative.ca----">>start_geopix_Log.txt
@echo "4)--Downloading TouchDesigner Installer from Derivative.ca----"

:: Download the installer with wget, logging along the way.
start "" /WAIT /B %td_download_exec_str%

:: FOR DEBUGGING - Simulate downloading by copying to directory from somewhere else.
rem copy "C:\Users\envir\Downloads\TouchDesigner.2020.28110.exe" "C:\Users\envir\OneDrive\Desktop\GEOPIX ON GITHUB\GeoPix\.tmp\TouchDesigner.2020.28110.exe"

:: If the td path doesn't exist, which it shouldn't at this point because we deleted it above, start the installation for that location.
if not exist "%td_path_abs%" (
    start "" /WAIT %td_installer_executable_abs% /SILENT /LOG="td_installation_Log.txt" /DIR="%td_path_abs%" /SUPPRESSMSGBOXES
    
    SET td_executable_path="%td_path_abs%\bin\TouchDesigner.exe"
    
    @echo "5)--TouchDesigner.%td_year%.%td_version% installed locally, proceeding to launch----">>start_geopix_Log.txt
    @echo "5)--TouchDesigner.%td_year%.%td_version% installed locally, proceeding to launch----"
    
    :: delete the tmp directory after we're done with install or anything else pre launch.
    if exist "%tmp_path_abs%" (
        del /S /Q "%tmp_path_abs%" 
        rmdir /S /Q "%tmp_path_abs%" 
    )
)


:ReadyToLaunch


:: Log some things
@echo "6)--Running the library asset downloader script, first time runs can take a little while----">>start_geopix_Log.txt
@echo "6)--Running the library asset downloader script, first time runs can take a little while----"
:: run the library asset downloader batch script.

CALL %library_fetch_script_path_abs%

:: Log some things
@echo "7)--TouchDesigner.%td_year%.%td_version% found, launching----">>start_geopix_Log.txt
@echo "7)--TouchDesigner.%td_year%.%td_version% found, launching----"

:: start geopix with locally installed td.
start "" %td_executable_path% %gp_executable_path_abs%

:: Log some things
@echo "8)--GeoPix has been launched, closing bootstrapper----">>start_geopix_Log.txt
@echo "8)--GeoPix has been launched, closing bootstrapper----"
TIMEOUT /T 5
