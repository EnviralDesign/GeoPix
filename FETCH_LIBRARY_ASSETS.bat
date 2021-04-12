:: turn off echo, so we only print intentional user messages.
@echo off

:: use this to break the script at this point, and not go any further
rem exit /b 1

:: change current working cmd directory to the root where batch executes from.
:: NOTE we might be able to nix this if we expand all our paths to absolute..
cd /d %~dp0

:: set this for proper variable expansion in for loops.
setlocal enableDelayedExpansion

:: wipe and reinit our log, with blank.
break>library_downloader_Log.txt

:: log some things
@echo.
@echo "=======================================">>library_downloader_Log.txt
@echo "====== BEGIN Library Fetch Script =====">>library_downloader_Log.txt
@echo "=======================================">>library_downloader_Log.txt
@echo "======================================="
@echo "====== BEGIN Library Fetch Script ====="
@echo "======================================="

:: Define the absolute path to the wget executable, bundled with GeoPix.
SET wget_executable_path=%~dp0GP\Utilities\wget.exe

:: Define the target directory for our LIBRARY downloads.
:: NOTE, this directory SHOULD exist already.
rem SET library_destination_directory=%~dp0.tmp
SET library_destination_directory=%~dp0GP\LIBRARY

:: define URL to the files.php script that returns our files_list data.
SET url_prefix=http://www.enviral-design.com/downloads/20_PREREQUISITES
SET files_list_url=%url_prefix%/files.php

:: Set the abs path to the files_list file. it might not exist yet.
SET file_list_path=%library_destination_directory%\file_list

:: Define some final variables
SET files_list_getter_string="%wget_executable_path%" -nv --show-progress -a library_downloader_Log.txt -P "%library_destination_directory%" "%files_list_url%"

:: Log some things.
@echo "2)--Downloading files list from remote server----">>library_downloader_Log.txt
@echo "2)--Downloading files list from remote server----"


:: Delete the file_list file, if it exists so we can re download a new one.
IF EXIST %file_list_path% (
	del %file_list_path%
)

:: Download the file_list from the php query page.
start "" /WAIT /B %files_list_getter_string%

:: Log some things.
@echo "3)--Renaming downloaded file to 'files_list'----">>library_downloader_Log.txt
@echo "3)--Renaming downloaded file to 'files_list'----"

:: Rename the retrieved file to something more sensible for local file system.
REN "%library_destination_directory%\files.php" file_list

:: Log some things.
@echo "4)--Downloading any missing library assets'----">>library_downloader_Log.txt
@echo "4)--Downloading any missing library assets'----"



:: For each line (that isn't blank apparently?) do what's in the brackets.
for /f "tokens=* delims=" %%a in ('type "%file_list_path%"') do (

	rem :: make a variable for this particular line of the file.
	SET line=%%a

	rem :: create full source URL to asset file on web.
	SET source_url=%url_prefix%/!line!
	
	rem :: create the absolute path to the file, that will be created locally after download.
	SET dest_file_path_abs=!library_destination_directory!/!line!
	

	rem :: do a find replace converting any forward slashes to back slashes.
	SET dest_file_path_abs=!dest_file_path_abs:/=\!

	rem :: update the variable to the parent directory of that file to be. this directory doesn't have to exist yet.
	rem :: NOTE: remember we need to use quotes here, because some of the paths might have spaces in them.
	for %%F in ("!dest_file_path_abs!") do SET dest_file_path_abs=%%~dpF

	rem :: %%~dpF returns the parent folder, but with a trailing slash. 
	rem :: this command cuts off the last character which will be that slash.
	SET dest_file_path_abs=!dest_file_path_abs:~0,-1!

	rem :: assemble the entire getter string for the asset, that downloads it to it's proper place locally.
	SET getter_exec_str="!wget_executable_path!" -nv --show-progress -a library_downloader_Log.txt -nc -P "!dest_file_path_abs!" "!source_url!"

	rem :: we need to check and see if the line is a blank line with just a space in it, and skip the wget operation if so.
	rem :: problem is.. we can't just test the !line! variable to a " " it doesn't work.. so work around was to encapsulate
	REM :: the string between two random characters, and test that.. works for some reason.
	if NOT "<!line!>" == "< >" (
		start "" /WAIT /B !getter_exec_str!
	)
	
)

:: Delete the files_list file after we're done with the downloading.
del "%library_destination_directory%\file_list"

:: Log some things.
@echo "5)--Finished fetching library assets!'----">>library_downloader_Log.txt
@echo "5)--Finished fetching library assets!'----"


:: log some things
@echo "=====================================">>library_downloader_Log.txt
@echo "====== END Library Fetch Script =====">>library_downloader_Log.txt
@echo "=====================================">>library_downloader_Log.txt
@echo "====================================="
@echo "====== END Library Fetch Script ====="
@echo "====================================="