#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Plugin Name: FileInfo
# Plugin URL: https://gitlab.com/w3labkr/python-fileinfo
# Plugin Version: 1.2.0 (Optimized)
# Plugin Author: w3labkr
# Plugin Author URL: https://w3lab.kr
# License: MIT License
#
# Description: Scans a directory recursively, collects information
#              about files (name and size), filters out specified
#              patterns, and saves the list to a text file.
#

import os
import sys

# --- Configuration ---

# The root directory to scan
TARGET_DIRECTORY = './example'

# The unit for file size representation ('Byte', 'KB', 'MB', 'GB', 'TB')
SIZE_UNIT = 'MB'

# List of substrings. If a file's full path contains any of these,
# it will be excluded. Useful for ignoring hidden files, specific
# extensions, directories, or specific filenames.
# Note: This checks for the substring anywhere in the full path.
EXCLUDE_PATTERNS = ['/.git/', '.DS_Store', 'README.md', '.png', '.txt', '.md']

# Output filename within the target directory
OUTPUT_FILENAME = 'fileinfo_optimized.txt'

# --- Constants ---
BYTES_PER_KB = 1024.0
BYTES_PER_MB = BYTES_PER_KB ** 2
BYTES_PER_GB = BYTES_PER_KB ** 3
BYTES_PER_TB = BYTES_PER_KB ** 4

# --- Functions ---

def format_file_size(size_in_bytes, unit='MB'):
    """
    Formats the file size into the specified unit.

    Args:
        size_in_bytes (int): File size in bytes.
        unit (str): The target unit ('Byte', 'KB', 'MB', 'GB', 'TB').
                    Defaults to 'MB'. Case-insensitive.

    Returns:
        str: Formatted file size string (e.g., "12.34MB") or
             original bytes if unit is invalid.
    """
    unit_lower = unit.lower()
    try:
        if unit_lower == 'byte':
            return f"{size_in_bytes} Bytes"
        elif unit_lower == 'kb':
            return f"{size_in_bytes / BYTES_PER_KB:.2f} KB"
        elif unit_lower == 'mb':
            return f"{size_in_bytes / BYTES_PER_MB:.2f} MB"
        elif unit_lower == 'gb':
            return f"{size_in_bytes / BYTES_PER_GB:.2f} GB"
        elif unit_lower == 'tb':
            return f"{size_in_bytes / BYTES_PER_TB:.2f} TB"
        else:
            # Default or unknown unit, return bytes
            print(f"Warning: Invalid size unit '{unit}'. Defaulting to Bytes.", file=sys.stderr)
            return f"{size_in_bytes} Bytes"
    except ZeroDivisionError:
         # Handle potential division by zero if constants were 0, though unlikely
         return "0 Bytes"
    except Exception as e:
        print(f"Error formatting size {size_in_bytes} with unit {unit}: {e}", file=sys.stderr)
        return f"{size_in_bytes} Bytes" # Fallback


def should_exclude(file_path, patterns):
    """
    Checks if the file path should be excluded based on the patterns.

    Args:
        file_path (str): The full path to the file.
        patterns (list): A list of substrings to check for exclusion.

    Returns:
        bool: True if the path contains any of the patterns, False otherwise.
    """
    return any(pattern in file_path for pattern in patterns)

# --- Main Execution ---

def main():
    """
    Main function to scan directory, collect file info, and write output.
    """
    if not os.path.isdir(TARGET_DIRECTORY):
        print(f"Error: Target directory '{TARGET_DIRECTORY}' not found or is not a directory.", file=sys.stderr)
        sys.exit(1) # Exit with an error code

    file_info_list = []

    print(f"Scanning directory: {TARGET_DIRECTORY}")
    print(f"Excluding paths containing: {EXCLUDE_PATTERNS}")
    print(f"Calculating size in: {SIZE_UNIT}")

    try:
        # os.walk is efficient for traversing directory trees
        for dirpath, _, filenames in os.walk(TARGET_DIRECTORY):
            for filename in filenames:
                # Construct the full path safely using os.path.join
                full_path = os.path.join(dirpath, filename)

                # Check if the path should be excluded
                if not should_exclude(full_path, EXCLUDE_PATTERNS):
                    try:
                        # Get file size
                        file_size_bytes = os.path.getsize(full_path)
                        # Format the size
                        formatted_size = format_file_size(file_size_bytes, SIZE_UNIT)

                        # Get path relative to the target directory for output consistency
                        # Prepend '/' to match original output format
                        relative_path = '/' + os.path.relpath(full_path, TARGET_DIRECTORY)

                        # Use OS-agnostic path separators in the output for consistency
                        relative_path = relative_path.replace(os.path.sep, '/')

                        # Add to list
                        file_info_list.append(f"{relative_path}, {formatted_size}")

                    except OSError as e:
                        print(f"Warning: Could not access or get size for '{full_path}': {e}", file=sys.stderr)
                    except Exception as e:
                         print(f"Warning: An unexpected error occurred processing file '{full_path}': {e}", file=sys.stderr)

    except Exception as e:
        print(f"Error during directory traversal: {e}", file=sys.stderr)
        sys.exit(1)


    # --- Export Results ---
    if not file_info_list:
        print("No files found matching the criteria.")
        return # Don't create an empty file if nothing was found

    # Construct the output file path safely
    output_file_path = os.path.join(TARGET_DIRECTORY, OUTPUT_FILENAME)

    try:
        # Use 'with open' for safer file handling (automatic close)
        # Specify encoding for broader compatibility
        with open(output_file_path, "w", encoding='utf-8') as f_out:
            # Join the list elements with ',\n'
            output_content = ',\n'.join(file_info_list)
            f_out.write(output_content)
        print(f"Successfully wrote file information to: {output_file_path}")

    except IOError as e:
        print(f"Error: Could not write to output file '{output_file_path}': {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during file writing: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()