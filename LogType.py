import enum

class LogType(enum.IntFlag):
    Info = 1
    Warning = 2
    Error = 3
    Success = 4
    pass