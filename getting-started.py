# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 11:57:58 2021

@author: Bjarne Gerdes
"""

import subprocess
import sys
import os
from zipfile import ZipFile

# install required packages
subprocess.check_call([sys.executable, "-m", "pip", "install", "gdown"])

# download models from google drive
import gdown

url = 'https://drive.google.com/uc?id=1UI35fBPJyF3mIJKP-6W4dP3Sl3acMTCK'
output = 'modelle.zip'
gdown.download(url, output, quiet=False) 

# unzip models
zip = ZipFile(output)
zip.extractall()
zip.close()

# remove zip file
os.remove(output)

# print docker-compose commands:
print("\n"*10)
print("Please execute the following using the cmd")
print("docker-compose -f ./src/docker-compose.yml build")
print("docker-compose -f ./src/docker-compose.yml up -d")