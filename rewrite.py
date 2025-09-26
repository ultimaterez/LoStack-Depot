#!/usr/bin/env python3

"""
Script to comment / edit lines in docker-compose.yml files
within the /packages/ directory structure.
"""

import os
import sys
import glob
import shutil
from datetime import datetime
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'  # No Color


def print_info(message):
    """Print info message in green."""
    print(f"{Colors.GREEN}[INFO]{Colors.NC} {message}")


def print_warning(message):
    """Print warning message in yellow."""
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")


def print_error(message):
    """Print error message in red."""
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")


def find_docker_compose_files():
    """Find all docker-compose.yml files in packages subdirectories."""
    packages_dir = Path("packages")
    
    if not packages_dir.exists():
        print_error("packages/ directory not found in current directory")
        sys.exit(1)
    
    if not packages_dir.is_dir():
        print_error("packages/ exists but is not a directory")
        sys.exit(1)
    
    # Find all docker-compose.yml files recursively
    pattern = packages_dir / "**/docker-compose.yml"
    files = list(Path().glob(str(pattern)))
    
    return files

def process_file(file_path):
    """
    Process a single docker-compose.yml file and comment out lines containing ".rule=Host(`".
    Returns the number of lines modified.
    """
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        modified_lines = 0
        new_lines = []
        
        for line in lines:
            # Check if line contains ".rule=Host(`" and is not already commented
            if '.rule=Host(`' in line and not line.strip().startswith('#'):
                # Comment out the line by adding "# " at the beginning
                # Preserve original indentation
                stripped = line.lstrip()
                indent = line[:len(line) - len(stripped)]
                commented_line = f"{indent}# {stripped}"
                new_lines.append(commented_line)
                modified_lines += 1
            elif 'traefik.enable=true' in line:
                line = line.replace("traefik.enable=true", "lostack.enable=true")
                new_lines.append(line)
                modified_lines += 1
            elif 'sablier.enable=true' in line:
                line = line.replace("sablier.enable=true", "lostack.enable_sablier=true")
                new_lines.append(line)
                modified_lines += 1
            elif 'sablier.group' in line:
                line = line.replace("sablier.group", "lostack.group")
                new_lines.append(line)
                modified_lines += 1
            elif 'server.port' in line:
                # Extract port number from the line
                port = line.split("=")[1].strip()
                # Get the indentation from the original line
                stripped = line.lstrip()
                indent = line[:len(line) - len(stripped)]
                # Create new lostack.port label with same indentation
                new_line = f"{indent}- lostack.port={port}\n"
                new_lines.append(new_line)
                modified_lines += 1
            elif 'lostack.duration' in line:
                line = line.replace("lostack.duration", "lostack.default_duration")
                new_lines.append(line)
                modified_lines += 1
            elif 'lostack.enable_sablier' in line:
                line = line.replace("lostack.enable_sablier", "lostack.autostart")
                new_lines.append(line)
                modified_lines += 1
            elif "lostack.port" in line:
                port = line.split("=")[1].strip().replace('"', "")
                # Get the indentation from the original line
                stripped = line.lstrip()
                indent = line[:len(line) - len(stripped)]
                # Create new lostack.port label with same indentation
                new_line = f"{indent}- lostack.port={port}\n"
                new_lines.append(new_line)
                modified_lines += 1
            else:
                new_lines.append(line)
        
        # Write back to file if modifications were made
        if modified_lines > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
        
        return modified_lines
        
    except Exception as e:
        print_error(f"Error processing file {file_path}: {e}")
        return -1  # Indicate error


def main():
    """Main function to orchestrate the script execution."""
    print_info("Starting to process docker-compose.yml files...")
    
    # Find all docker-compose.yml files
    docker_files = find_docker_compose_files()
    
    if not docker_files:
        print_warning("No docker-compose.yml files found in packages/ subdirectories")
        return
    
    # Counters for summary
    files_found = len(docker_files)
    files_modified = 0
    total_lines_commented = 0
    
    # Process each file
    for file_path in docker_files:
        print_info(f"Processing: {file_path}")
        
        # Check file permissions
        if not os.access(file_path, os.R_OK | os.W_OK):
            print_error(f"Cannot read/write file: {file_path}")
            continue
                
        # Process the file
        modified_lines = process_file(file_path)
        
        if modified_lines == -1:  # Error occurred
            continue
        elif modified_lines > 0:
            files_modified += 1
            total_lines_commented += modified_lines
            print_info(f"Modified {modified_lines} lines in {file_path}")
    
    # Print summary
    print()
    print_info("=== SUMMARY ===")
    print_info(f"Files found: {files_found}")
    print_info(f"Files modified: {files_modified}")
    print_info(f"Total lines commented: {total_lines_commented}")
    
    print_info("Script completed successfully!")


if __name__ == "__main__":
    main()