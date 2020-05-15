class IdChangeError(Exception):
    def __init__(self, code=100, message='数据变动', args=('数据变动',)):
        self.args = args
        self.message = message
        self.code = code
