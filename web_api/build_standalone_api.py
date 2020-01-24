#!/usr/bin/env python

"""
Run PyInstaller, and then some post processing
"""

import shutil
from subprocess import run
from pathlib import Path

dist_dir = Path("dist").absolute() / "run_web_api"

# run pyInstaller:

# maybe need to set some other options, defaults for now
run(["pyinstaller", "-y", "run_web_api.py"])

# A total hack to get the full cornice package in:

# print("copying the cornice package in")
import cornice

cornice_dir = Path(cornice.__file__).parent

# copy the cornice dir in:

shutil.rmtree(dist_dir / "cornice", ignore_errors=True)
shutil.copytree(cornice_dir, dist_dir / "cornice")

# find dist-info dir
dist_info_dir = next(cornice_dir.parent.glob('cornice*dist-info'))
dist_info_name = dist_info_dir.parts[-1]

# and copy it in
shutil.rmtree(dist_dir / dist_info_name, ignore_errors=True)
shutil.copytree(dist_info_dir, dist_dir / dist_info_name)





print("dist-info:")
print(dist_info_dir)




