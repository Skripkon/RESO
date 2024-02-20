#!/bin/bash

directory="../generated_data"
extensions=("*.mid" "*.mp3")
threshold=0 # Specifies the threshold (in days)

# Find files with specified extensions that were created more than 1 day ago
files_to_remove=""
for extension in "${extensions[@]}"; do
    files_to_remove+="$(find ../generated_data/ -type f -name "$extension" -ctime $threshold)"
done

# Loop through the files and remove them
count=0
for file in $files_to_remove; do
	count=$((count+1))
	echo "	Removed file ${file}"
    rm $file
done

echo "$count ${extensions[*]} files older than $threshold days have been removed from $directory"