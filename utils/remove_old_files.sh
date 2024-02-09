#!/bin/bash

directory="../generated_data"
extensions=("*.mid" "*.mp3")
threshold=1 # Specifies the threshold (in days)

# Change to the directory specified
cd $directory

# Find files with specified extensions that were created more than 1 day ago
files_to_remove=""
for extension in "${extensions[@]}"; do
    files_to_remove+="$(find . -type f -name "$extension" -mtime +$threshold) "
done

# Loop through the files and remove them
count=0
for file in $files_to_remove; do
	count+=1
	echo "	Removed file ${file}"
    rm $file
done

echo "$count ${extensions[*]} files older than $threshold days have been removed from $directory"