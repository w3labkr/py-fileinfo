# FileInfo

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Version](https://img.shields.io/badge/version-1.4.1-blue)

A Python script to recursively scan a directory, gather file information (relative path and size), filter out unwanted files/directories based on path patterns, and save the results to a text file. Useful for tasks like generating file manifests or analyzing disk usage patterns.

**Author:** [w3labkr](https://w3labkr.github.io/)
**Source:** [https://github.com/w3labkr/py-fileinfo](https://github.com/w3labkr/py-fileinfo)

## Features

* **Recursive Scanning:** Traverses through all subdirectories of a target directory.
* **File Information:** Collects relative file paths and calculates file sizes.
* **Flexible Size Units:** Formats file sizes into Bytes, KB, MB, GB, or TB.
* **Path-Based Filtering:** Excludes files or directories if their **full absolute path** contains specified substring patterns.
* **Command-Line Interface:** Easily configurable through command-line arguments.
* **Text File Output:** Saves the filtered list of files and their sizes to a specified text file.
* **Quiet Mode:** Option to suppress informational messages during execution.
* **Error Handling:** Reports warnings (stderr) for non-critical file access issues (e.g., permission denied, file not found) and continues scanning. Exits on critical errors (e.g., target directory not found, output file write failure).
* **Symbolic Link Handling:** By default, follows symbolic links during directory traversal (`os.walk` default). Be cautious with recursive links. If needed, modify the script to use `followlinks=False` in the `os.walk` call.

## Requirements

* Python 3.x. Ensure Python 3 is installed and accessible from your command line (e.g., check `python3 --version`).

## Installation

1.  Clone the repository or download the `fileinfo.py` script.
    ```bash
    # If using Git
    git clone [https://github.com/w3labkr/py-fileinfo.git](https://github.com/w3labkr/py-fileinfo.git)
    cd py-fileinfo
    ```
    Alternatively, just save the script code as `fileinfo.py`.
2.  No external package installation is required.

## Usage

Run the script from your terminal using `python3`.

**Note:** By default, the script scans the current directory (`.`). Use the `-d` option to specify a different directory.

### Basic Syntax

```bash
python3 fileinfo.py [options]
```

### Options

| Argument            | Default                                                              | Description                                                                                                                               |
| :------------------ | :------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------- |
| `-h`, `--help`      |                                                                      | Show the help message and exit.                                                                                                           |
| `-d`, `--directory` | `.`                                                                  | The target directory to scan recursively. **Must exist.** |
| `-u`, `--unit`      | `MB`                                                                 | The unit for displaying file sizes. Choices: `Byte`, `KB`, `MB`, `GB`, `TB`.                                                              |
| `-o`, `--output`    | `output.txt`                                                         | The name of the output file. This file is created **inside** the target directory (`-d`).                                                   |
| `-e`, `--exclude`   | `['/.git/', '/node_modules/', '/__pycache__/', '.DS_Store', 'Thumbs.db']` | Substring pattern to exclude. **Checks the full path**. Can be specified multiple times to *add* patterns to the default list.           |
| `-q`, `--quiet`     | `False`                                                              | Suppress informational messages (scan parameters, completion summary). Warnings and errors are still shown.                               |

### Examples

1.  **Run with defaults (scan current directory):**
    ```bash
    python3 fileinfo.py
    ```
    *(Output file will be `./output.txt`)*

2.  **Scan a specific directory, use KB, and set a custom output file name:**
    ```bash
    python3 fileinfo.py -d /path/to/your/data -u KB -o file_list_kb.txt
    ```
    *(Output file will be `/path/to/your/data/file_list_kb.txt`)*

3.  **Scan the current directory (`.`) and add `.log` and `/temp/` to the exclusion list:**
    ```bash
    python3 fileinfo.py -d . -e .log -e /temp/
    ```
    *(This will exclude defaults AND paths containing `.log` or `/temp/`)*

4.  **Run a quiet scan using GB units:**
    ```bash
    python3 fileinfo.py -d /mnt/storage -u GB -q
    ```

## Output Format

The script generates a text file (specified by `-o`, default `fileinfo.txt`) inside the target directory (`-d`). Each line in this file represents a file that was **not** excluded and follows the format:

```
/relative/path/to/file, Formatted Size Unit
```

**Example (`fileinfo.txt` content):**

```
/documents/report_final.docx, 1.52 MB
/media/videos/holiday_compilation.mp4, 780.21 MB
/archive.zip, 1024.00 MB
/code/main_script.py, 0.05 MB
```

* The path starts with `/` and represents the path relative to the scanned directory (`-d`).
* Path separators are always `/`, regardless of the operating system.
* The size is formatted to two decimal places with the chosen unit (`-u`).

## Exclusion Behavior

* The `-e` or `--exclude` patterns are checked against the **full absolute path** of each file encountered during the scan.
* **Important:** Exclusion is based on a simple **substring match**. If any specified pattern exists *anywhere* within the full path string of a file, that file will be excluded.
    * Example: If `.tmp` is an exclusion pattern:
        * `/home/user/data/file.tmp` -> Excluded.
        * `/home/user/my.tmp.folder/data.txt` -> Excluded (because `.tmp` is in the path).
        * `/home/user/temporary/file.txt` -> **Not** excluded by `.tmp` (unless another pattern matches).
    * Example: If `/.git/` is excluded, any file whose full path contains `/.git/` (like `/path/to/project/.git/config`) will be excluded.
* Be specific with your patterns for accurate filtering (e.g., use `/node_modules/` or `.git/` with slashes for directories, or precise filenames like `.DS_Store`).
* Specifying `-e` multiple times **adds** patterns to the default list: `['/.git/', '/node_modules/', '/__pycache__/', '.DS_Store', 'Thumbs.db']`. There is currently no command-line option to *replace* the default list entirely without modifying the script's code.

## License

This project is licensed under the [MIT License](LICENSE).
