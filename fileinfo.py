#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Plugin Name: FileInfo
# Plugin URL: https://github.com/w3labkr/py-fileinfo
# Plugin Version: 1.4.1 (Refactored with Generator)
# Plugin Author: w3labkr
# Plugin Author URL: https://w3labkr.github.io/
# License: MIT License
#
# Description: Scans a directory recursively, collects information
#              about files (name and size), filters out specified
#              patterns, and saves the list to a text file.
#              Accepts command-line arguments for configuration.
#

import os
import sys
import argparse

# --- Constants ---
BYTES_PER_KB = 1024.0
BYTES_PER_MB = BYTES_PER_KB ** 2
BYTES_PER_GB = BYTES_PER_KB ** 3
BYTES_PER_TB = BYTES_PER_KB ** 4

# --- Helper Functions ---

def format_file_size(size_in_bytes, unit='MB'):
    """Formats the file size into the specified unit."""
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
            print(f"Warning: Invalid size unit '{unit}'. Defaulting to Bytes.", file=sys.stderr)
            return f"{size_in_bytes} Bytes"
    except ZeroDivisionError:
         return "0 Bytes"
    except Exception as e:
        print(f"Error formatting size {size_in_bytes} with unit {unit}: {e}", file=sys.stderr)
        return f"{size_in_bytes} Bytes"

def should_exclude(file_path, filename, patterns):
    """
    Checks if the file path or filename should be excluded based on patterns.

    Args:
        file_path (str): The full path to the file.
        filename (str): The name of the file itself.
        patterns (list): A list of substrings to check for exclusion.

    Returns:
        bool: True if the path contains any pattern, False otherwise.

    --- IMPORTANT ---
    Current behavior: Performs a simple substring check. If any pattern
    exists ANYWHERE within the FULL file path (file_path), it returns True.
    This can be broad. For example, if '.txt' is a pattern, paths like:
        '/path/to/archive.txt.zip'
        '/home/user/my_texts/document.pdf'
    would BOTH be excluded. Be specific with patterns (e.g., '/.git/', '.DS_Store').

    --- Alternative Filtering Examples (Modify if needed) ---
    # 1. Exclude by exact filename match:
    # if filename in patterns:
    #     return True

    # 2. Exclude by file extension:
    # _, ext = os.path.splitext(filename)
    # if ext and ext in patterns: # Ensure patterns list contains extensions like '.log', '.tmp'
    #     return True

    # 3. Check pattern only against filename (not full path):
    # if any(pattern in filename for pattern in patterns):
    #      return True
    """
    if not patterns:
        return False
    try:
        # Default: Check substring in the full path
        return any(pattern in file_path for pattern in patterns)
    except TypeError as e:
        print(f"Error: Invalid pattern detected. Ensure all patterns are strings: {e}", file=sys.stderr)
        return True # Exclude if pattern check fails

def scan_files(target_directory, exclude_patterns, size_unit, quiet_mode):
    """
    Scans the directory and yields information about included files.

    Args:
        target_directory (str): The root directory to scan.
        exclude_patterns (list): List of patterns for exclusion.
        size_unit (str): The unit for file size.
        quiet_mode (bool): Suppress warnings if True.

    Yields:
        tuple: (relative_path, formatted_size) for each included file.

    Returns:
        tuple: (total_files_scanned, errors_encountered)
    """
    files_scanned = 0
    errors_encountered = 0

    # Note: os.walk follows symbolic links by default. Use followlinks=False if needed.
    for dirpath, _, filenames in os.walk(target_directory):
        for filename in filenames:
            files_scanned += 1
            full_path = os.path.join(dirpath, filename)

            # Pass both full_path and filename to should_exclude for flexibility
            if not should_exclude(full_path, filename, exclude_patterns):
                try:
                    file_size_bytes = os.path.getsize(full_path)
                    formatted_size = format_file_size(file_size_bytes, size_unit)
                    relative_path = '/' + os.path.relpath(full_path, target_directory)
                    relative_path = relative_path.replace(os.path.sep, '/')

                    yield (relative_path, formatted_size)

                except FileNotFoundError:
                    if not quiet_mode:
                         print(f"Warning: File not found (possibly deleted): '{full_path}'", file=sys.stderr)
                    errors_encountered += 1
                except PermissionError:
                     if not quiet_mode:
                          print(f"Warning: Permission denied: '{full_path}'", file=sys.stderr)
                     errors_encountered += 1
                except OSError as e:
                    if not quiet_mode:
                         print(f"Warning: OS error accessing '{full_path}': {e}", file=sys.stderr)
                    errors_encountered += 1
                except Exception as e:
                     if not quiet_mode:
                         print(f"Warning: Unexpected error processing '{full_path}': {e}", file=sys.stderr)
                     errors_encountered += 1

    return files_scanned, errors_encountered

def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Scan directory for file information and save to a file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-d", "--directory", default='.',
        help="The target directory to scan recursively."
    )
    parser.add_argument(
        "-u", "--unit", default='MB', choices=['Byte', 'KB', 'MB', 'GB', 'TB'],
        help="The unit for displaying file sizes."
    )
    parser.add_argument(
        "-o", "--output", default='output.txt',
        help="The name of the output file (created inside the target directory)."
    )
    parser.add_argument(
        "-e", "--exclude", action='append',
        default=['/.git/', '/node_modules/', '/__pycache__/', '.DS_Store', 'Thumbs.db'],
        help="Substring patterns to exclude (checks full path). "
             "Can be specified multiple times. Example: -e /.git/ -e .tmp"
    )
    parser.add_argument(
        "-q", "--quiet", action='store_true',
        help="Suppress informative messages (warnings/errors still shown)."
    )
    return parser.parse_args()

# --- Main Execution ---

def main():
    """
    Parses arguments, scans directory using generator, collects results, and writes output.
    """
    args = parse_arguments()

    target_directory = args.directory
    size_unit = args.unit
    exclude_patterns = args.exclude
    output_filename = args.output
    quiet_mode = args.quiet

    if not os.path.isdir(target_directory):
        print(f"Error: Target directory '{target_directory}' not found or is not a directory.", file=sys.stderr)
        sys.exit(1)

    if not quiet_mode:
        print(f"Scanning directory: {os.path.abspath(target_directory)}")
        print(f"Excluding paths containing: {exclude_patterns}")
        print(f"Calculating size in: {size_unit}")
        print(f"Output file name: {output_filename}")
        print("-" * 20)

    # Initialize variables
    file_info_list = []
    files_scanned = 0
    errors_encountered = 0

    try:
        # Call the function that builds the list and returns counts
        file_info_list, files_scanned, errors_encountered = \
            build_file_list(target_directory, exclude_patterns, size_unit, quiet_mode)

    except Exception as e:
        print(f"Error during file scanning process: {e}", file=sys.stderr)
        sys.exit(1)

    # --- Export Results ---
    files_included = len(file_info_list)

    if not file_info_list:
        if not quiet_mode:
            print("-" * 20)
            print(f"Scan complete. No files found matching the criteria in '{target_directory}'.")
            # Ensure counts are displayed even if no files are included
            print(f"(Total files scanned: {files_scanned}, Errors: {errors_encountered})")
        return # Exit cleanly if no files were included

    output_file_path = os.path.join(target_directory, output_filename)

    try:
        with open(output_file_path, "w", encoding='utf-8') as f_out:
            # Join with newline and comma for each entry
            output_content = '\n'.join(file_info_list)
            f_out.write(output_content)
            # Add a trailing newline if desired (optional)
            # f_out.write('\n')


        if not quiet_mode:
            print("-" * 20)
            print(f"Scan complete. Successfully wrote {files_included} file entries to: {output_file_path}")
            print(f"(Total files scanned: {files_scanned}, Included: {files_included}, Errors: {errors_encountered})")

    except IOError as e:
        print(f"Error: Could not write to output file '{output_file_path}': {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during file writing: {e}", file=sys.stderr)
        sys.exit(1)


# --- Refactored Function to Build List (instead of pure generator) ---
def build_file_list(target_directory, exclude_patterns, size_unit, quiet_mode):
    """
    Scans the directory, builds a list of included file info, and returns counts.
    Note: This version collects all results in memory.
    """
    files_scanned = 0
    errors_encountered = 0
    results_list = []

    # Note: os.walk follows symbolic links by default. Use followlinks=False if needed.
    for dirpath, _, filenames in os.walk(target_directory):
        for filename in filenames:
            files_scanned += 1
            full_path = os.path.join(dirpath, filename)

            if not should_exclude(full_path, filename, exclude_patterns):
                try:
                    file_size_bytes = os.path.getsize(full_path)
                    formatted_size = format_file_size(file_size_bytes, size_unit)
                    relative_path = '/' + os.path.relpath(full_path, target_directory)
                    relative_path = relative_path.replace(os.path.sep, '/')
                    results_list.append(f"{relative_path}, {formatted_size}")

                except FileNotFoundError:
                    if not quiet_mode: print(f"Warning: File not found (possibly deleted): '{full_path}'", file=sys.stderr)
                    errors_encountered += 1
                except PermissionError:
                     if not quiet_mode: print(f"Warning: Permission denied: '{full_path}'", file=sys.stderr)
                     errors_encountered += 1
                except OSError as e:
                    if not quiet_mode: print(f"Warning: OS error accessing '{full_path}': {e}", file=sys.stderr)
                    errors_encountered += 1
                except Exception as e:
                     if not quiet_mode: print(f"Warning: Unexpected error processing '{full_path}': {e}", file=sys.stderr)
                     errors_encountered += 1

    return results_list, files_scanned, errors_encountered


if __name__ == "__main__":
    main()