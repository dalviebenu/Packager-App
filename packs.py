from manifest import *
from texts import Texts
from utils import *


def mk_pack(folder_name, name, manifest_type, declaration_name, folders=(), json_files=(), manifest_args=(),
            txt_args=None, **_):
    #args are from .json files in packager.
    if txt_args is None:
        txt_args = {}

    class Pack:
        ICON_NAME = 'pack_icon.png'
        copy_jsons = json_files
        copy_dirs = folders
        folder = folder_name
        declaration_file = declaration_name

        @staticmethod
        def get_txt_args(fargs):
            return {k: v.format(**fargs) for k, v in txt_args.items()}

        def __init__(self, icon, fargs, copy_manifest=None, texts=None, min_engine_version=None, **copy_paths):
            if icon is None:
                raise NoPackIconError()

            self.pack_icon = icon
            self.pack_icon.convert(S_SQ)

            self.fargs = fargs

            self.texts = texts

            self.uuid = uuid4()
            self.manifest = Manifest(self.uuid, manifest_type, copy_manifest=copy_manifest,
                                     min_engine_version=min_engine_version)

            for param in self.copy_dirs:
                setattr(self, param, none_or_path(copy_paths.get(param)))
                # creates class objects from param with value from dict with key param. (multiple paths)

            for param in self.copy_jsons:
                setattr(self, param, copy_paths.get(param))

            self.declaration = PackDeclaration(self.uuid)

        @classmethod
        def load(cls, path, icon, fargs, languages=None, min_engine_version=None):
            path = Path(path)

            copy_paths = {
                name: path / name if (path / name).is_dir() else None
                for name in cls.copy_dirs
            }
            # creates a dict with name : path for values from folders in the json files.

            for json_param in cls.copy_jsons:
                json_path = path / json_param
                if json_path.is_file():
                    copy_paths[json_param] = load_json(json_path)
                    # add the keys from json_files with its the json contents to copy_paths.

            copy_manifest = Manifest.get_copy_manifest(path / 'manifest.json', manifest_args)

            texts = cls.get_texts(path, fargs, languages)

            return cls(icon, fargs, copy_manifest=copy_manifest, texts=texts,
                       min_engine_version=min_engine_version, **copy_paths)
            # this is when those loops param run since at this point copy_paths has all values.

        @classmethod
        def get_texts(cls, path, fargs, languages=None):
            path = path / 'texts'
            if path.is_dir():
                texts, errors = Texts.load(path, languages=languages, default_content=cls.get_txt_args(fargs))

                if not errors.is_empty():
                    print(errors)

            else:
                texts = Texts(languages=languages, default_content=cls.get_txt_args(fargs))

            return texts

        def write(self, path):
            self.declaration.write(path / self.declaration_file)

            pack_path = Path(path) / folder_name / name.format(**self.fargs)
            create(pack_path)

            self.pack_icon.write(pack_path / self.ICON_NAME)
            self.manifest.write(pack_path)
            self.texts.write(pack_path)

            for param in self.copy_dirs:
                src_path = getattr(self, param)
                if src_path:
                    copypath(src_path, pack_path / param)

            for param in self.copy_jsons:
                obj = getattr(self, param)
                if obj:
                    write_json(pack_path / param, obj)

    return Pack


class NoPackIconError(Exception):
    def __str__(self):
        return 'No Pack Icon (S7.jpg file) was found.'


pack_args = frozenset({
    'folders', 'json_files', 'manifest_args', 'name', 'folder_name', 'manifest_type', 'txt_args', 'declaration_name'
})
# immutable

packs = []

for pack in src_dir.glob('Pack Descriptions/*.json'): # returns json files stored in folder in packager
    obj = load_json(pack)

    if not pack_args.issuperset(obj.keys()):
        print('Warning: Unknown arguments in {}:\n\t{}'.format(pack, ', '.join(obj.keys() - pack_args)))

    packs.append(mk_pack(**obj))
