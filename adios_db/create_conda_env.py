#!/usr/bin/env python
import sys
import subprocess

USAGE = """
create_conda_env.py environment_name [run|test|all]

create a conda environment for the adios_db project

saves typing in all the requirements files

default is "run" -- full dev environment

"run" will only give you wnat you need to run the code without mongodb

"test will give you want you need to run the tests (without mongo)

"all" will install everything for running and testing with mongodb

NOTE: currently hard-coded for Python 3.10
"""

if __name__ == "__main__":
    try:
        env_name = sys.argv[1]
    except IndexError:
        print(USAGE)
        sys.exit(1)

    argv = sys.argv[2:]
    reqs = ["conda_requirements.txt"]

    if "test" in argv or "all" in argv:
        reqs.append("conda_requirements_test.txt")

    if "all" in argv:
        reqs.append("conda_requirements_optional.txt")
        reqs.append("docs_requirements.txt")

    cmd = ["conda", "create", "-n", env_name, "python=3.10"]

    for req in reqs:
        cmd.extend(["--file", req])

    print("running\n", cmd)
    subprocess.run(cmd)




