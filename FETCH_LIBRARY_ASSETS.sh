#!/bin/bash

# Turn off echo, so we only print intentional user messages.
set +x

# Change the current working directory to the directory where the script executes from.
# NOTE: We might be able to remove this if we use absolute paths.
cd "$(dirname "$0")"

# Log some things.
echo ""
echo "=======================================" >> library_downloader_Log.txt
echo "====== BEGIN Library Fetch Script =====" >> library_downloader_Log.txt
echo "======================================="
echo "====== BEGIN Library Fetch Script ====="
echo "======================================="

# Define the target directory for our LIBRARY downloads.
# NOTE: This directory SHOULD exist already.
library_destination_directory="$PWD/GP/LIBRARY"

# Define URL to the files.php script that returns our files_list data.
url_prefix="http://www.enviral-design.com/downloads/20_PREREQUISITES"
files_list_url="${url_prefix}/files.php"

# Set the absolute path to the files_list file. It might not exist yet.
file_list_path="${library_destination_directory}/file_list"

# Log some things.
echo "2) -- Downloading files list from the remote server ----" >> library_downloader_Log.txt
echo "2) -- Downloading files list from the remote server ----"

# Delete the file_list file if it exists so we can re-download a new one.
if [ -e "$file_list_path" ]; then
    rm "$file_list_path"
fi

# Download the file_list from the php query page.
wget -nv --show-progress -a library_downloader_Log.txt -P "$library_destination_directory" "$files_list_url"

# Log some things.
echo "3) -- Renaming downloaded file to 'files_list' ----" >> library_downloader_Log.txt
echo "3) -- Renaming downloaded file to 'files_list' ----"

# Rename the retrieved file to something more sensible for the local file system.
mv "${library_destination_directory}/files.php" "$file_list_path"

# Log some things.
echo "4) -- Downloading any missing library assets ----" >> library_downloader_Log.txt
echo "4) -- Downloading any missing library assets ----"

# Read the file_list line by line and download the assets.
while IFS= read -r line || [ -n "$line" ]; do
    # Check if the line is not blank.
    if [ -n "${line}" ]; then
        source_url="${url_prefix}/${line}"
        dest_file_path_abs="${library_destination_directory}/${line}"
        dest_file_path_abs="$(dirname "$dest_file_path_abs")"

        echo "Downloading: ${source_url}"

        # Download the asset.
        wget -nv --show-progress -a library_downloader_Log.txt -nc -P "$dest_file_path_abs" "$source_url"
    fi
done < "$file_list_path"

# Delete the file_list file after we're done with the downloading.
rm "$file_list_path"

# Log some things.
echo "5) -- Finished fetching library assets! ----" >> library_downloader_Log.txt
echo "5) -- Finished fetching library assets! ----"

# Log some things.
echo "=====================================" >> library_downloader_Log.txt
echo "====== END Library Fetch Script =====" >> library_downloader_Log.txt
echo "====================================="
echo "====== END Library Fetch Script ====="
echo "====================================="
