import casc
#from distutils.core import run_setup

with casc.Casc( "E:\\myGames\\World of Warcraft" ) as c:
    handler, result = c.find_first_file("*")
    while True:
        handler, result = c.find_next_file(handler)
        if not handler:
            print("last file")
            break
        if result['filename'].endswith(".m2"):
            print(result)
        #print( "파일 : " , result['filename'] )

with casc.Casc("E:\\myGames\\Warcraft3") as cf:
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
