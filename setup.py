import os
import sys
import subprocess
import pathlib
import shutil
import configparser

mode = 'Debug'  # Debug/Release
plat = 32
os.environ['DISTUTILS_DEBUG'] = "1" if mode == 'Debug' else ""

from setuptools import Extension, setup
from distutils.util import get_platform

extensions = []
script_args = []
if not sys.argv[1] == 'install':
    if not (pathlib.Path(__file__) / '..' / 'CascLib').is_dir():
        print("didn't find CascLib, cloning from repo...")
        subprocess.run(["git", "clone", "https://github.com/ladislav-zezula/CascLib.git"])

    bname32 = 'build86'
    bname64 = 'build'
    build64_dir = pathlib.Path(__file__) / '..' / 'CascLib' / bname32
    build32_dir = pathlib.Path(__file__) / '..' / 'CascLib' / bname64
    buil_dir = {32: build32_dir, 64: build64_dir}.get(plat, build64_dir)
    cmake_opts = {32: ["-A", "Win32"], 64: ["-A", "x64"]}.get(plat, [])
    setup_build_plat = {32: 'win32', 64: 'win-amd64'}.get(plat, get_platform())
    bname = {32: bname32, 64: bname64}.get(plat, bname64)

    include_dir = pathlib.Path(__file__) / '..' / 'CascLib' / 'src'
    print("build dir", str(buil_dir))

    shutil.rmtree(buil_dir / mode, ignore_errors=True)

    setup_cfg = configparser.ConfigParser()
    setup_cfg['build'] = {
        'plat-name': setup_build_plat,
        'debug': True if mode == 'Debug' else False
    }
    with (pathlib.Path(__file__) / '..' / 'setup.cfg').open('w') as cfg_file:
        setup_cfg.write(cfg_file)

    if not buil_dir.is_dir():
        print("didn't find CascLib build scaffolding, creating...")
        buil_dir.mkdir(exist_ok=True)
        subprocess.run([
            "cmake",
            "-DCASC_BUILD_SHARED_LIB:BOOL=OFF", "-DCASC_BUILD_STATIC_LIB:BOOL=ON", "-DCASC_UNICODE:BOOL=ON",
        ] + cmake_opts + [
            ".."
        ], cwd=buil_dir)
        buil_dir.mkdir(exist_ok=True)

    if not (buil_dir / mode).is_dir():
        print("Now building", plat, "bits zezula casclib")
        subprocess.run([
            "cmake", "--build", ".",
            "--config", mode,
            # "--clean-first",
            "--verbose" if mode == "Debug" else ""
        ], cwd=buil_dir)

    print("argc", sys.argv)
    print("fetching libraries from", str((buil_dir / mode).resolve()))
    extensions.append(
        Extension(
            "_casc",
            sources=['casc.c'],
            include_dirs=[str(include_dir)],
            library_dirs=[str((buil_dir / mode).resolve())],
            define_macros=[('CASCLIB_NO_AUTO_LINK_LIBRARY', None)],
            libraries=['casc'],
        )
    )

setup(
    name='casc',
    py_modules=['casc'],
    ext_modules=extensions,
    verbose=mode == 'Debug',
)
