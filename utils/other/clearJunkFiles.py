from glob import glob
import os

items = ["*.flv", "*.mp4", "*.f4v", "../*.flv", "../*.mp4", "../*.pyc", "../*.download"]
for item in items:
    for file in glob(item):
        if os.path.exists(file):
            os.remove(file)

