from utils import *
from typing import Tuple, Union
from pathlib import Path
from PIL import Image as PILImage


class WrongResolutionError(Exception):
    def __init__(self, path: Path, expected: Tuple[int, int], found: Tuple[int, int]):
        self.path = path
        self.expected = expected
        self.found = found

    def __str__(self):
        return 'Wrong resolution for image "{}". Expected {}, found {}'.format(self.path, self.expected, self.found)


class Image:
    @staticmethod
    def is_valid_res(res, expected):
        for i in range(2):
            if type(expected[i]) == range:
                if res[i] not in expected[i]:
                    return False
            elif res[i] != expected[i]:
                return False

        return True

    def __init__(self, path: Path, resolution: Tuple[Union[int, range], Union[int, range]]):
        self.img = PILImage.open(path)

        self.modified = False

        if not self.is_valid_res(self.img.size, resolution):
            raise WrongResolutionError(path, resolution, self.img.size)

        self.path = path

    def write(self, path: Path):
        if self.modified:
            self.img.save(path, quality=95)
        else:
            copypath(self.path, path)

    def convert(self, size):
        if size == self.img.size:
            pass

        self.img.resize(size, PILImage.LANCZOS)
        self.modified = True
