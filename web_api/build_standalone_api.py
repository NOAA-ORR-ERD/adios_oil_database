#!/usr/bin/env python

"""
Run PyInstaller, and then some post processing
"""

import shutil
from subprocess import run
from pathlib import Path

extra_modules = ['pkg_resources.py2_warn',
                 'pyramid_tm',
                 'cornice',
                 'pyramid_mongodb2',
#                 'oil_database_api.views',
# these to try to get config.scan() to work -- but alas ...
#                  'oil_database_api.views.capabilities',
#                  'oil_database_api.views.distinct',
# #                 'oil_database_api.views.oil',  # this causes an infinite recursion
#                  'oil_database_api.views.category',
#                  'oil_database_api.views.query',
                 ]

hidden_imports = []
for mod in extra_modules[:]:
    hidden_imports.append('--hidden-import')
    hidden_imports.append(mod)


api_name = "run_web_api"
# note: the start_server script was uglier to get running under PyInstaller
#       so I punted on that.
# api_name = "start_server"
api_script = api_name + ".py"


dist_dir = Path("dist").absolute()
web_api_dir = dist_dir / api_name


# run pyInstaller:

# maybe need to set some other options, defaults for now
cmd = ["pyinstaller", "-y",]
cmd.append("--clean")
if hidden_imports:
    cmd.extend(hidden_imports)
cmd.append(api_script)
print(cmd)
run(cmd)

# run(["pyinstaller", "-y", api_script, "simple_server.py"])

# # this seems to pull the dependencies from simple_server, but not
# # create a startup stub -- so we build it again
# # PyInstaller supports  multipackage builds, but it looks really ugly.
# run(["pyinstaller", "-y", "simple_server.py"])

# # then copy the simple_server stub to the run_web_api dir
# shutil.copy(dist_dir / "simple_server" / "simple_server", web_api_dir)
# # delete it to save confusion?
# shutil.rmtree(dist_dir / "simple_server", ignore_errors=True)


# # A total hack to get the full cornice package in:
# # This not neccesary if you use the NOAA-ORR-ERD fork of cornice
# print("copying the cornice package in")
# import cornice

# cornice_dir = Path(cornice.__file__).parent

# # copy the cornice dir in:

# shutil.rmtree(web_api_dir / "cornice", ignore_errors=True)
# shutil.copytree(cornice_dir, web_api_dir / "cornice")

# # find dist-info dir
# dist_info_dir = next(cornice_dir.parent.glob('cornice*dist-info'))
# dist_info_name = dist_info_dir.parts[-1]

# # and copy it in
# shutil.rmtree(web_api_dir / dist_info_name, ignore_errors=True)
# shutil.copytree(dist_info_dir, web_api_dir / dist_info_name)
