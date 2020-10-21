import os
import sys

mode = 'Debug'  # Debug/Release
plat = 32
os.environ['DISTUTILS_DEBUG'] = "1" if mode == 'Debug' else ""

from setuptools import Extension, setup, find_packages
from distutils.util import get_platform
import subprocess
import pathlib
import shutil



if not (pathlib.Path('.') / 'CascLib').is_dir():
    subprocess.run(["git", "clone", "https://github.com/ladislav-zezula/CascLib.git"])

build64_dir = pathlib.Path('.') / 'CascLib' / 'build'
build32_dir = pathlib.Path('.') / 'CascLib' / 'build86'
buil_dir = {32: build32_dir, 64: build64_dir}.get(plat, build64_dir)
cmake_opts = {32: ["-A", "Win32"], 64: ["-A", "x64"]}.get(plat, [])
setup_build_plat = {32: 'win32', 64: 'win-amd64'}.get(plat, get_platform())

include_dir = pathlib.Path('.') / 'CascLib' / 'src'
print("build dir", str(buil_dir))


shutil.rmtree(pathlib.Path('.') / 'build', ignore_errors=True)
shutil.rmtree(buil_dir / mode, ignore_errors=True)

if not buil_dir.is_dir():
    buil_dir.mkdir(exist_ok=True)
    subprocess.run([
        "cmake",
        "-DCASC_BUILD_SHARED_LIB:BOOL=OFF", "-DCASC_BUILD_STATIC_LIB:BOOL=ON", "-DCASC_UNICODE:BOOL=ON",
    ] + cmake_opts + [
        ".."
    ], cwd=buil_dir)
    buil_dir.mkdir(exist_ok=True)

if not (buil_dir / mode).is_dir():
    print("build", plat, "bits zezula casclib")
    subprocess.run([
        "cmake", "--build", ".",
        "--config", mode,
        # "--clean-first",
        "--verbose" if mode == "Debug" else ""
    ], cwd=buil_dir)

print("argc", sys.argv)

setup(
    name='casc',
    py_modules=['casc'],
    ext_modules=[
        Extension(
            "_casc",
            sources=['casc.c'],
            include_dirs=[str(include_dir)],
            library_dirs=[str((buil_dir / mode).resolve())],
            define_macros=[('CASCLIB_NO_AUTO_LINK_LIBRARY', None)],
            libraries=['casc'],
            language='c++',
        )
    ],
    verbose=True,
    packages=['casclib'],
    package_dir={'casclib': 'CascLib'},
    package_data={'casclib': ['build/'+mode+'/*']},
    script_args=['build', f'--plat-name={setup_build_plat}', f"--debug" if mode == 'Debug' else "", "bdist-wheel"] if len(sys.argv) == 1 else sys.argv[1:],
)
