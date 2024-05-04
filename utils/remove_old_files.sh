#!/bin/bash

directory="generated_data/"
extensions=("*.mid" "*.mp3" "*.pdf" "*.musicxml")
threshold=$1 # Get the threshold from the argument (in minutes)

# Find files with specified extensions that were created more than 1 day ago
files_to_remove=""
for extension in "${extensions[@]}"; do
    files_to_remove+=" $(find "$directory" -type f -name "$extension" -cmin +$threshold)"
done

# Loop through the files and remove them
count=0
for file in $files_to_remove; do
	count=$((count+1))
	echo "	Removed file ${file}"
    rm $file
done

echo "$count ${extensions[*]} files last edited more than $threshold minutes ago have been removed from $directory"