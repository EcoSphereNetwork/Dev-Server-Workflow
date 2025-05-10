#!/bin/bash

# Script to identify and remove all .bak.20250509124941 backup files
# Created as part of the Dev-Server-Workflow repository cleanup project

echo "Identifying all .bak.20250509124941 backup files..."
BACKUP_FILES=$(find . -name "*.bak.20250509124941")
BACKUP_COUNT=$(echo "$BACKUP_FILES" | wc -l)

echo "Found $BACKUP_COUNT backup files to remove."

# Create a backup list file for reference
echo "Creating a list of backup files for reference..."
echo "$BACKUP_FILES" > backup_files_list.txt
echo "Backup file list saved to backup_files_list.txt"

# Ask for confirmation before removing files
read -p "Do you want to proceed with removing these backup files? (y/n): " confirm

if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
    echo "Removing backup files..."
    find . -name "*.bak.20250509124941" -delete
    echo "Backup files have been removed."
else
    echo "Operation cancelled. No files were removed."
fi