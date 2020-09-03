#!/usr/bin/env python3
import sys
from utils.version_check import Update

# Make sure python 3 is being used
if sys.version_info[0] < 3:
    print('\033[91mERROR:\033[0m you must be running python 3.0 or higher.')
    sys.exit()

# Defaults
NAME = 'TrailerTechnician'
VERSION = '1.0.0'
DESCRIPTION = 'Download trailers for your local movie library.'

# Check for updates
update = Update()
update.run()