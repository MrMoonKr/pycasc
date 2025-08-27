import os
import sys
import subprocess
import pathlib
import shutil
import configparser
import platform
import sysconfig

mode = 'Release'  # Debug/Release
plat = 32 if platform.architecture()[0] == '32bit' else 64  # 32 or 64
os.environ['DISTUTILS_DEBUG'] = "1" if mode == 'Debug' else ""

from setuptools import Extension, setup
#from distutils.util import get_platform
#from distutils.ccompiler import new_compiler

extensions = []
print("setup.py mode", sys.argv[1] if len(sys.argv) > 1 else "none")
print("platform", sys.platform, platform.architecture())
print("cmdline", sys.argv)

if not sys.argv[1] == 'install':
    if not (pathlib.Path('.') / 'CascLib').is_dir():
        print("didn't find CascLib, cloning from repo...")
        subprocess.run(["git", "clone", "https://github.com/ladislav-zezula/CascLib.git"])

    bname32 = 'build86'
    bname64 = 'build64'
    buil_dir = {
        32: pathlib.Path('.') / 'CascLib' / bname32,
        64: pathlib.Path('.') / 'CascLib' / bname64}.get(plat)
    cmake_opts = {32: ["-A", "Win32"], 64: ["-A", "x64"]}.get(plat, [])
    # setup_build_plat = {32: 'win32', 64: 'win-amd64'}.get(plat, get_platform())
    setup_build_plat = {32: 'win32', 64: 'win-amd64'}.get(plat, sysconfig.get_platform())
    bname = {32: bname32, 64: bname64}.get(plat, bname64)

    include_dir = pathlib.Path('.') / 'CascLib' / 'src'
    
    print("build dir", str(buil_dir))

    shutil.rmtree(buil_dir, ignore_errors=True)

    setup_cfg = configparser.ConfigParser()

    setup_cfg['build'] = {
        'plat_name': setup_build_plat,
        'debug': True if mode == 'Debug' else False
    }

    with (pathlib.Path('.') / 'setup.cfg').open('w') as cfg_file:
        setup_cfg.write(cfg_file)  # needed?

    if not buil_dir.is_dir():
        print("didn't find CascLib build scaffolding, creating...")
        buil_dir.mkdir(exist_ok=True)
        subprocess.run([
            "cmake",
            "-DCASC_BUILD_SHARED_LIB:BOOL=OFF", "-DCASC_BUILD_STATIC_LIB:BOOL=ON", "-DCASC_UNICODE:BOOL=OFF", "-DCMAKE_POLICY_VERSION_MINIMUM=3.5"
        ] + cmake_opts + [
            ".."
        ], cwd=buil_dir)
    else:
        print("Found build dir, skipping")

    if not (buil_dir / mode).is_dir():
        print("Now building", plat, "bits zezula casclib")
        subprocess.run([
            "cmake", "--build", ".",
            "--config", mode,
            "--clean-first",
            "--verbose"
        ], cwd=buil_dir)
    else:
        print("Not building zezulas casclib")

    print("argc", sys.argv)
    print("fetching libraries from", str((buil_dir / mode).resolve()))
    print("Fetching environment paths")

    extensions.append(
        Extension(
            "_casc",
            sources=['casc.c'],
            include_dirs=[
                str(include_dir)
            ] ,
            library_dirs=[str((buil_dir / mode).resolve())],
            define_macros=[('CASCLIB_NO_AUTO_LINK_LIBRARY', None), ('_WIN32', '1') if plat == 32 else ('_WIN64', '1')],
            libraries=['casc'],
        )
    )

setup(
    name='casc',
    version='0.0.1',
    url='https://github.com/Meithal/pycasc',
    py_modules=['casc'],
    ext_modules=extensions,
    verbose=mode == 'Debug',
    description="Python library that binds to CascLib used by Blizzards games",
    long_description=''.join([l for l in open('README.md')]),
    long_description_content_type='text/markdown',
)
