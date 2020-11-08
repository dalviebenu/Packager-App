# Installs the needed packages to run the packaging script

import subprocess
import sys

executable = sys.executable


def install(package):
    subprocess.run([executable, '-m', 'pip', 'install', package])


subprocess.run([executable, '-m', 'pip', 'install', '--upgrade', 'pip'])

install('pillow')
install('numpy')
