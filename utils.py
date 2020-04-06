import json
import re
from functools import reduce
from pathlib import Path
from shutil import copy2
import numpy as np
from os import path
import zipfile
import os

src_dir = Path(path.realpath(__file__)).parent

HD = (1920, 1080)
MEDIUM = (800, 450)
L_SQ = (256, 256)  # Large square
S_SQ = (64, 64)  # Small square
PANORAMA = (range(1000, 4001), 450)
ANY = (range(1, 2 ** 60), range(1, 2 ** 60))


class FormattingArgs(dict):
    _keys = {
        'full_name': lambda name: name,
        'name': lambda name: name,
        'low_name': lambda name: lower_name(name),
        'up_name': lambda name: upper_name(name),
        'short_name': lambda name: short_name(lower_name(name))
    }

    def __init__(self, name, **kwargs): # we pass name and fullname in product.py
        for key, fct in self._keys.items():
            if key not in kwargs: # if key not in kwargs then make a new element in kwargs with key and fct(name)
                kwargs[key] = fct(name)

        super().__init__(**kwargs)

    def __setitem__(self, key, value):
        if key not in self._keys:
            raise KeyError(key)

        else:
            super().__setitem__(key, self._keys[key](value))
        # returns a dict with the keys in _keys and values filled using the functions in _keys.


def deep_update(d, u):
    for k, v in u.items():
        if isinstance(d, dict):
            if isinstance(v, dict):
                r = deep_update(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        else:
            d = {k: u[k]}
    return d


def create(p):
    if not p.exists():
        p.mkdir(parents=True)


def copypath(src, dst):
    # copies what is in src to dir.
    if src.is_file():
        create(dst.parent)
        copy2(src, dst)

    elif src.is_dir():
        create(dst)
        for p in src.iterdir():
            copypath(p, dst / p.name)


def none_or_path(obj):
    if obj is None:
        return None

    return Path(obj)


def write_json(path, obj):
    with open(path, 'w', encoding='UTF-8') as f:
        json.dump(obj, f, sort_keys=True, indent=2)


def load_json(path):
    try:
        with open(path, 'r', encoding='UTF-8') as f:
            return json.load(f)

    except json.JSONDecodeError as e:
        raise JSONError(path, e)


class JSONError(Exception):
    def __init__(self, path, error):
        self.path = path
        self.error = error

    def __str__(self):
        return 'Error while opening JSON file "{}":\n{}'.format(self.path, self.error)


def skin_lower(name):
    return '-'.join(re.split(r'[ _]', name.lower()))


def lower_name(name):
    return name.lower().replace(' ', '_')


def upper_name(name):
    return ''.join(map(str.capitalize, name.split()))


def short_name(name, length=6):
    if len(name) > length:
        name = name[:length]

    return name


def is_world(path: Path):
    return (path / 'levelname.txt').is_file()


def is_pack(path: Path):
    return (path / 'manifest.json').is_file()


def color_code(color):
    if len(color) == 4 and color[3] == 0:
        return 0

    return reduce(lambda x, y: (int(x) << 8) | y, color, 0)


def get_pixel_matrix(img):
    data = img.getdata()
    return np.asarray([color_code(c) for c in np.asarray(data)], dtype=np.uint32).reshape(
        (img.width, img.height))

def zip_file(loc, dst):
    # Make zip of packaged files, will be placed in the parent folder to prevent replication of zip in zip file.
    abs_src = path.abspath(loc)
    with zipfile.ZipFile(dst + '.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
        for folderName, subfolder, filenames in os.walk(loc):
            for filename in filenames:
                file_path = path.abspath(os.path.join(folderName, filename))
                arcname = file_path[len(abs_src) + 1:]
                zf.write(file_path, arcname)
