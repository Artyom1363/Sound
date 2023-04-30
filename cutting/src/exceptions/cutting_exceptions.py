class BadRequest(Exception):
    '''
    Exceptions raises if request of redundant is invalid
    '''

    def __init__(self, message='Bad request'):
        super().__init__(message)
