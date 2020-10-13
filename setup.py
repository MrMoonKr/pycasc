from setuptools import Extension, setup, find_packages
import subprocess
import pathlib
import shutil

mode = 'Debug'

if not (pathlib.Path('.') / 'CascLib').is_dir():
    subprocess.run(["git", "clone", "https://github.com/ladislav-zezula/CascLib.git"])

buil_dir = pathlib.Path('.') / 'CascLib' / 'build'
include_dir = pathlib.Path('.') / 'CascLib' / 'src'

# shutil.rmtree(pathlib.Path('.') / 'build', ignore_errors=True)
# shutil.rmtree(buil_dir / mode, ignore_errors=True)

if not buil_dir.is_dir():
    buil_dir.mkdir(exist_ok=True)
    subprocess.run([
        "cmake",
        "-DCASC_BUILD_SHARED_LIB:BOOL=OFF", "-DCASC_BUILD_STATIC_LIB:BOOL=ON", "-DCASC_UNICODE:BOOL=ON",
        ".."
    ], cwd=buil_dir)

if not (buil_dir / mode).is_dir():
    subprocess.run([
        "cmake", "--build", ".",
        "--config", mode,
        # "--clean-first",
        "--verbose"
    ], cwd=buil_dir)

module = Extension(
    "_casc",
    sources=['casc.c'],
    include_dirs=[str(include_dir)],
    library_dirs=[str((buil_dir / mode).resolve())],
    define_macros=[('CASCLIB_NO_AUTO_LINK_LIBRARY', None)],
    libraries=['casc'],
)

setup(name='casc', ext_modules=[module], verbose=True)
