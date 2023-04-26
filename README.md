Dependencies
---

- `git` in PATH
- `cmake` in PATH
- Visual Studio build tools or a C compiler 
able to build python extensions on your 
platform https://visualstudio.microsoft.com/fr/visual-cpp-build-tools/
- `pip install check-wheel-contents`

Install
---

```shell
python ./setup.py build
```

Create wheel

```shell
python ./setup.py bdist_wheel
```