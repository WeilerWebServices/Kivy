#!C:/Users/natew/Desktop/Flask_To_Do_App/my_kivy_project/bin/python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'coverage==5.0.4','console_scripts','coverage3'
__requires__ = 'coverage==5.0.4'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('coverage==5.0.4', 'console_scripts', 'coverage3')()
    )
