import enum


class FfmpegState(enum.IntFlag):
    Found = 1
    NotFound = 3
    pass
