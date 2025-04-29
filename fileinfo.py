#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Plugin Name: FileInfo
# Plugin URL: https://gitlab.com/w3labkr/python-fileinfo
# Plugin Version: 1.3.0 (Optimized with CLI args)
# Plugin Author: w3labkr
# Plugin Author URL: https://w3lab.kr
# License: MIT License
#
# Description: Scans a directory recursively, collects information
#              about files (name and size), filters out specified
#              patterns, and saves the list to a text file.
#              Accepts command-line arguments for configuration.
#

import os
import sys
import argparse # For command-line arguments

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
                    Case-insensitive.

    Returns:
        str: Formatted file size string (e.g., "12.34MB") or
             original bytes if unit is invalid.
    """
    unit_lower = unit.lower()
    try:
        if unit_lower == 'byte':
            # Keep Bytes as integer for precision if possible
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
        return f"{size_in_bytes} Bytes" # Fallback

def should_exclude(file_path, patterns):
    """
    Checks if the file path should be excluded based on the patterns.
    IMPORTANT: This function performs a simple substring check. If any pattern
               exists anywhere within the full file path, it returns True.
               For example, if '.txt' is a pattern, '/path/to/archive.txt.zip'
               and '/home/user/my_texts/document.pdf' would both be excluded.
               Be specific with your patterns (e.g., use '/.git/' instead of '.git').

    Args:
        file_path (str): The full path to the file.
        patterns (list): A list of substrings to check for exclusion.

    Returns:
        bool: True if the path contains any of the patterns, False otherwise.
    """
    if not patterns: # Handle case where no patterns are provided
        return False
    try:
        return any(pattern in file_path for pattern in patterns)
    except TypeError as e:
        print(f"Error: Invalid pattern detected in exclusion list. Ensure all patterns are strings: {e}", file=sys.stderr)
        # Decide whether to continue without this pattern or exit
        # For safety, let's exclude the file if we can't check patterns reliably
        return True # Or False, depending on desired behavior on pattern error


def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Scan directory for file information and save to a file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter # Show defaults in help
    )
    parser.add_argument(
        "-d", "--directory",
        default='./example', # Default directory
        help="The target directory to scan recursively."
    )
    parser.add_argument(
        "-u", "--unit",
        default='MB', # Default size unit
        choices=['Byte', 'KB', 'MB', 'GB', 'TB'], # Allowed choices
        help="The unit for displaying file sizes."
    )
    parser.add_argument(
        "-o", "--output",
        default='fileinfo.txt', # Default output filename
        help="The name of the output file (will be created inside the target directory)."
    )
    parser.add_argument(
        "-e", "--exclude",
        action='append', # Allows specifying multiple times: -e .git -e .DS_Store
        default=['/.git/', '.DS_Store', 'README.md', '.png', '.txt', '.md'], # Default exclude patterns
        help="Substring patterns to exclude. Files whose full path contains any of these "
             "patterns will be ignored. Can be specified multiple times."
             " Example: -e /.git/ -e .tmp -e node_modules"
    )
    parser.add_argument(
        "-q", "--quiet",
        action='store_true', # Flag, True if present
        help="Suppress informative messages (warnings and errors are still shown)."
    )

    return parser.parse_args()

# --- Main Execution ---

def main():
    """
    Main function to parse arguments, scan directory, collect file info, and write output.
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

    file_info_list = []

    if not quiet_mode:
        print(f"Scanning directory: {os.path.abspath(target_directory)}")
        print(f"Excluding paths containing: {exclude_patterns}")
        print(f"Calculating size in: {size_unit}")
        print(f"Output file name: {output_filename}")
        print("-" * 20) # Separator

    files_scanned = 0
    files_included = 0
    errors_encountered = 0

    try:
        # os.walk is efficient for traversing directory trees
        for dirpath, _, filenames in os.walk(target_directory):
            for filename in filenames:
                files_scanned += 1
                # Construct the full path safely using os.path.join
                full_path = os.path.join(dirpath, filename)

                # Check if the path should be excluded
                if not should_exclude(full_path, exclude_patterns):
                    try:
                        # Get file size
                        file_size_bytes = os.path.getsize(full_path)
                        # Format the size
                        formatted_size = format_file_size(file_size_bytes, size_unit)

                        # Get path relative to the target directory for output consistency
                        # Prepend '/' to match original output format
                        relative_path = '/' + os.path.relpath(full_path, target_directory)

                        # Use OS-agnostic path separators in the output for consistency
                        relative_path = relative_path.replace(os.path.sep, '/')

                        # Add to list
                        file_info_list.append(f"{relative_path}, {formatted_size}")
                        files_included += 1

                    except FileNotFoundError:
                        # File might have been deleted between os.walk and os.path.getsize
                        if not quiet_mode:
                             print(f"Warning: File not found during size check (possibly deleted): '{full_path}'", file=sys.stderr)
                        errors_encountered += 1
                    except PermissionError:
                         if not quiet_mode:
                              print(f"Warning: Permission denied to access '{full_path}'", file=sys.stderr)
                         errors_encountered += 1
                    except OSError as e:
                        # Catch other potential OS errors related to file access
                        if not quiet_mode:
                             print(f"Warning: Could not access or get size for '{full_path}': {e}", file=sys.stderr)
                        errors_encountered += 1
                    except Exception as e:
                         if not quiet_mode:
                             print(f"Warning: An unexpected error occurred processing file '{full_path}': {e}", file=sys.stderr)
                         errors_encountered += 1
                # else: # Optional: Log excluded files if needed for debugging
                    # if not quiet_mode:
                    #     print(f"Debug: Excluding file: {full_path}")

    except Exception as e:
        print(f"Error during directory traversal: {e}", file=sys.stderr)
        sys.exit(1)


    # --- Export Results ---
    if not file_info_list:
        if not quiet_mode:
            print("-" * 20)
            print(f"Scan complete. No files found matching the criteria in '{target_directory}'.")
            print(f"(Total files scanned: {files_scanned}, Errors: {errors_encountered})")
        return # Don't create an empty file if nothing was found

    # Construct the output file path safely (inside the target directory)
    output_file_path = os.path.join(target_directory, output_filename)

    try:
        # Use 'with open' for safer file handling (automatic close)
        # Specify encoding for broader compatibility
        with open(output_file_path, "w", encoding='utf-8') as f_out:
            # Join the list elements with ',\n'
            output_content = ',\n'.join(file_info_list)
            f_out.write(output_content)

        if not quiet_mode:
            print("-" * 20)
            print(f"Scan complete. Successfully wrote {files_included} file entries to: {output_file_path}")
            print(f"(Total files scanned: {files_scanned}, Errors encountered: {errors_encountered})")

    except IOError as e:
        print(f"Error: Could not write to output file '{output_file_path}': {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during file writing: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()