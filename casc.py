import _casc


class Casc:
    def __init__( self, path ):
        self.path = path
        self.inst = None

    def __enter__( self ):
        self.inst = _casc.open( self.path )
        return self

    def __exit__( self, exc_type, exc_val, exc_tb ):
        _casc.close( self.inst )

    def find_first_file( self, mask ):
        return _casc.find_first_file( self.inst, mask )

    @staticmethod
    def find_next_file( handler ):
        return _casc.find_next_file( handler )

    @staticmethod
    def find_close_file( handler ):
        return _casc.find_close( handler )

    def open_file( self, name ):
        file_ =  _casc.open_file( self.inst, name )
        return file_

    def read_file( self, file_ ):
        red_ = _casc.read_file( file_ )
        return red_

    def close_file( self, file_ ):
        _casc.close_file( file_ )
        # return rv
