@echo off
setlocal enableDelayedExpansion
echo "---Begininng of Log---">START_log.txt

rem ### Define some TD version specific variables. TODO: pull these from files on disk?
SET tdYear=2020
SET tdVersion=28110
SET GeoPixExec=GeoPix_2.0.toe

rem ### Define some paths and strings and URLs
SET rootPath=%~dp0
SET wgetPath=GP\Utilities
SET fullWgetPath=%rootPath%%wgetPath%\wget.exe
SET fullTdPath=%rootPath%.td
SET fullTmpPath=%rootPath%.tmp
SET fullTdInstallerPath=%rootPath%.tmp\TouchDesigner.%tdYear%.%tdVersion%.exe
SET tdDownloadUrl="https://download.derivative.ca/TouchDesigner.%tdYear%.%tdVersion%.exe"
SET regQueryStr="HKEY_CLASSES_ROOT\TouchDesigner.%tdYear%.%tdVersion%\shell\open\command"
SET fullDownloaderExecStr=%fullWgetPath% -P %fullTmpPath% %tdDownloadUrl%
SET fullGpExecutablePath=%rootPath%GP\%GeoPixExec%
SET tdExecutablePath=

rem ### IF registry entry exists, get path to TD executable and set to variable tdExecutablePath
rem ### Next, trim off the last 5 characters to get the pure path. !! characters are used for DelayedExpansion

echo "Searching registry for matching, previously installed versions of TouchDesigner.%tdYear%.%tdVersion%...">>START_log.txt
@echo on
echo Searching registry for matching, previously installed versions of TouchDesigner.%tdYear%.%tdVersion%...
@echo off
rem TIMEOUT /T 1

reg query %regQueryStr% >nul
if %errorlevel% equ 0 (
    FOR /F "usebackq tokens=2,* skip=2" %%L IN (
        `reg query "%regQueryStr%"`
    ) DO SET tdExecutablePath=%%M
    SET tdExecutablePath=!tdExecutablePath:~0^,-5!
    if exist !tdExecutablePath! goto ReadyToLaunch
) else (
    goto InstallTD
)

:InstallTD
echo "Could not find any matching registry entries, installing TD locally...">>START_log.txt
@echo on
echo Could not find any matching registry entries, installing TD locally...
@echo off

if exist %fullTmpPath% (
    del /S /Q %fullTmpPath% 
    rmdir /S /Q %fullTmpPath% 
)
if exist %fullTdPath% (
    del /S /Q %fullTdPath% 
    rmdir /S /Q %fullTdPath% 
)

echo "Succesfully deleted .td and .tmp folders...">>START_log.txt
@echo on
echo Succesfully deleted .td and .tmp folders...
@echo off
rem TIMEOUT /T 5

mkdir %fullTmpPath%

rem ### DOWNLOAD TD WITH WGET
echo "Starting download of the TD installer...">>START_log.txt
start /WAIT /B %fullDownloaderExecStr%

rem ### SIMULATLE DOWNLOAD BY COPYING FROM DOWNLOADS DIRECTORY
rem copy C:\Users\envir\Downloads\TouchDesigner.2020.28110.exe C:\Users\envir\Documents\GitHub\GeoPix\.tmp\TouchDesigner.2020.28110.exe

if not exist %fullTdPath% (
    start /WAIT %fullTdInstallerPath% /SILENT /LOG="TdInstallation_Log.txt" /DIR=%fullTdPath% /SUPPRESSMSGBOXES
    SET tdExecutablePath=%fullTdPath%\bin\TouchDesigner.exe
    
    echo "TouchDesigner.%tdYear%.%tdVersion% installed locally, proceeding to launch...">>START_log.txt
    @echo on
    echo TouchDesigner.%tdYear%.%tdVersion% installed locally, proceeding to launch...
    @echo off

    if exist %fullTmpPath% (
        del /S /Q %fullTmpPath% 
        rmdir /S /Q %fullTmpPath% 
    )
)


:ReadyToLaunch

echo "TouchDesigner.%tdYear%.%tdVersion% found, launching...">>START_log.txt
@echo on
echo TouchDesigner.%tdYear%.%tdVersion% found, launching...
@echo off


start %tdExecutablePath% %fullGpExecutablePath%

echo "GeoPix has been launched, closing bootstrapper...">>START_log.txt
@echo on
echo GeoPix has been launched, closing bootstrapper...
@echo off
TIMEOUT /T 5
