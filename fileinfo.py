#
# Plugin Name: FileInfo
# Plugin URL: https://gitlab.com/w3labkr/python-fileinfo
# Plugin Version: 1.1.0
# Plugin Author: w3labkr
# Plugin Author URL: https://w3lab.kr
# License: MIT License
#

import os

def get_f_size(f_path,f_unit):
    f_size = os.path.getsize(f_path)
    if 'Byte' in f_unit:
        f_out = str(f_size) + 'Bytes'
    elif 'KB' in f_unit:
        f_out = str(f_size / 1024) + 'KB'
    elif 'MB' in f_unit:
        f_out = '%.2fMB' % (f_size / (1024.0 * 1024.0))
    return f_out

# Options
r_dir = './example'
f_unit = 'MB'
invaild = [ '/.git/', '.DS_Store', 'README', '.png', '.txt', '.md' ]

# __init__
txt = []
for r_file in os.listdir(r_dir):
    r_path = r_dir +'/'+ r_file
    if os.path.isfile(r_path):
        if not any(x in r_path for x in invaild):
            txt += [ '/'+ r_file +', '+ get_f_size(r_path,f_unit) ]
    elif os.path.isdir(r_path):
        # Get All of sub directory
        s_dirs = [x[0] for x in os.walk(r_path)]
        for s_dir in s_dirs:
            for s_file in os.listdir(s_dir):
                s_path = s_dir +'/'+ s_file
                if os.path.isfile(s_path):
                    if not any(x in s_path for x in invaild):
                        txt += [ s_dir.replace(r_dir,"") +'/'+ s_file +', '+ get_f_size(s_path,f_unit) ]

# Export
txt = ',\n'.join(txt)
txt_file = r_dir + '/fileinfo.txt'
txt_file = open(txt_file,"w")
txt_file.write(txt)
txt_file.close()
