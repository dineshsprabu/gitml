

class VersionMLException(Exception):
    def __init__(self, msg, cause=None):
        self.cause = cause
        self.cause_tb = traceback.format_exc() if cause else None
        super(VersionMLException, self).__init__(msg)
