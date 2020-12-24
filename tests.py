import casc
from distutils.core import run_setup



with casc.Casc("D:\\Warcraft III:w3") as cf:
    print("test.py, start search handler")
    handler, result = cf.find_first_file("*")
    print("test.py, first file", result)
    while True:
        handler, result = cf.find_next_file(handler)
        if not handler:
            print("last file")
            break
        if result['filename'].endswith(".slk"):
            print(result)
    status, file_ = cf.open_file("war3.w3mod:units\\unitdata.slk")
    if status:
        file_, content, actual_read = cf.read_file(file_)
        cf.close_file(file_)
        print(content)
    else:
        print("Something Wrong", file_)
