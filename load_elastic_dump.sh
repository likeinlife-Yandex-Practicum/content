#!/bin/sh
files_list=$(ls ./dumps)
for file in $files_list
do 
    index=$(echo $file | cut -d . -f 1)
    type=$(echo $file | cut -d . -f 3)
    elasticdump --input=/dumps/"$file" --output=http://${HOST}:${PORT}/"$index" --type="$type"
done