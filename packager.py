#!/usr/bin/env python

import argparse
from pathlib import Path
from utils import *
from product import Content


version = [1, 4, 3]


def pack(src, dst, name, uuid_w, uuid_s, version, **kwargs):
    # this simply creates a path object with useful methods
    src = Path(src)
    dest = Path(dst + '/contents')
    zip_loc = dst + '/contents'
    mcpack_loc = dst + '/contents/Content/world_template'
    mcpack_dst = dst + '/world_template'
    content = Content.load(src, name, uuid_w, uuid_s, version, **kwargs)
    content.write(dest)

    # Make zip of data and world_template
    zip_file(zip_loc, zip_loc)
    zip_file(mcpack_loc, mcpack_dst)

    pre, ext = os.path.splitext(dst + '/world_template.zip')
    os.rename(dst + '/world_template.zip', (str(dest.parent) + '/' + str(dest.parent.name) + '.mcpack'))

    print("\nFinished...")


arg_mapping = {
    'full-name': 'full_name',
    'skin-pack-name': 'skin_pack_name',
    'languages': 'languages'
}

parser = argparse.ArgumentParser(description='Package Bedrock content for the Marketplace')
parser.add_argument('src', help='Source path')
parser.add_argument('dst', help='Destination path')
parser.add_argument('--name', '-n', help='Name of the content', metavar='name')
parser.add_argument('--full-name', '-f', help='Complete name of the content', metavar='name')
parser.add_argument('--skin-pack-name', '-s', help='Name of the skin pack', metavar='name')
parser.add_argument('--languages', '-l', help='Languages supported', nargs='*', metavar='lang')
parser.add_argument('--version', '-V', action='version', version='%(prog)s ' + '.'.join(map(str, version)))

# if __name__ == '__main__':
    # Takes the arguments, switches the '-' for '_' and make it a dict. We then pass it to def pack.
#    args = parser.parse_args()
#    mod_args = {arg_mapping.get(key, key): value for key, value in args.__dict__.items()}
#    pack(**mod_args)
