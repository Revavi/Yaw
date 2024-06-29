# Yaw V2.0
# authors: Revavi, msihek, Chonnon
from os import path, mkdir
from shutil import rmtree

from core.interface.interface import run

if __name__ == "__main__":
    if path.isdir("temp"):
        rmtree("temp")
    
    if not path.isdir("config"):
        mkdir("config")

    run()