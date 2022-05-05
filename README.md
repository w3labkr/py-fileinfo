# FileInfo
Export all file names and file sizes in subdirectories to a txt file


## Output
in fileinfo.txt
```
/file-1, 320 KB,
/path-1/file-2, 150 KB,
/path-1/path-1-2/file-3, 120 KB,
/path-2/file-4, 290 KB,
```


## Options
```
r_dir = '/file/path' # (string)
f_unit = 'KB' # (string) 'Byte', 'KB', 'MB'
invaild = [ '/.git/', '.DS_Store', 'fileinfo.txt' ] # (array) directory or filename
```


## Usage
1. Open the fileinfo.py and change options
2. in Terminal
```
$ python /file/path/fileinfo.py
```


## Example
```
r_dir = '/Users/Username/Downloads'
f_unit = 'KB'
invaild = [ '/.git/', '.DS_Store', 'README', '.png', '.txt', '.md' ]
```


## Changelog
Please see [CHANGELOG](CHANGELOG) for more information what has changed recently.


## License
MIT License. Please see [License File](LICENSE) for more information.
