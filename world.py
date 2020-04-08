from packs import *


def check_base_game_version(tag):
    if isinstance(tag, list):
        while len(tag) < 3:
            tag.append(0)

        if len(tag) > 3:
            tag = tag[:3]

        return tag

    if isinstance(tag, str):
        if tag == '*':
            return tag

        return check_base_game_version(list(map(int, re.split(r'[,.]', tag))))


class World:
    copy_params = ('db', 'level.dat', 'levelname.txt')

    BP_NAME = 'behavior_packs'
    RP_NAME = 'resource_packs'

    ICON_NAME = 'world_icon.jpeg'
    BP_JSON = 'world_behavior_packs.json'
    RP_JSON = 'world_resource_packs.json'

    MANIFEST_DATA_CHECK = {
        'base_game_version': check_base_game_version
    }

    def __init__(self, icon, uuid, version, txt_args=None, languages=None, data_packs=(), copy_manifest=None,  **kwargs):
        if txt_args is None:
            txt_args = {}

        self.icon = icon
        self.version = version
        self.data_packs = data_packs

        for param in self.copy_params:
            setattr(self, param, kwargs.get(param))

        if uuid is not None:
            self.uuid = uuid
        else:
            self.uuid = uuid4()

        self.manifest = Manifest(self.uuid, Manifest.WORLD, version=self.version, copy_manifest=copy_manifest)

        self.texts = Texts(languages=languages, default_content=txt_args, copy_langs=None)

    @classmethod
    def load(cls, path: Path, world_icon, pack_icon, fargs, uuid_w=None, version=None, min_engine_version=None,
             languages=None, txt_args=None):

        args = {}  # Contains args for the creation of the World: behavior pack, resource pack and copy_params

        data_packs = []

        for pack in packs:
            pack_path = path / pack.folder
            # from packs file
            if path.is_dir():
                folders = list(filter(is_pack, pack_path.iterdir()))
                if len(folders) > 1:
                    raise MultiplePacksError(path)

                if len(folders) == 1:
                    data_packs.append(pack.load(pack_path / folders[0], pack_icon, fargs, languages, min_engine_version))

        for param in cls.copy_params:
            if (path / param).exists():
                args[param] = path / param

        # Retrieve data
        data = load_json(path / "packager_data.json")

        if 'texts' in data:
            txt_args.update(data['texts'])

        if 'manifest' not in data:
            raise PackagerDataMissingKeyError(path / "packager_data.json", 'manifest')

        for key, value in data['manifest'].items():
            if key in cls.MANIFEST_DATA_CHECK:
                data['manifest'][key] = cls.MANIFEST_DATA_CHECK[key](value)

        copy_manifest = {
            'header': data['manifest']
        }

        return cls(icon=world_icon, uuid=uuid_w, version=version, txt_args=txt_args, data_packs=data_packs,
                   copy_manifest=copy_manifest, **args)

    def write(self, path: Path):
        path = path / 'world_template'
        create(path)

        self.icon.write(path / self.ICON_NAME)

        self.manifest.write(path)

        for pack in self.data_packs:
            pack.write(path)

        self.texts.write(path)

        for param in self.copy_params:
            if getattr(self, param) is None:
                print('Missing file \"{}\" in world template'.format(param))

            else:
                copypath(getattr(self, param), path / param)


class MultiplePacksError(Exception):
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return 'Multiple pack folders found in "{}"'.format(self.path)


class PackagerDataMissingKeyError(Exception):
    def __init__(self, path, key):
        self.path = path
        self.key = key

    def __str__(self):
        return 'Missing key in packager_data.json in "{}"\n\tKey "{}" not found'.format(self.path, self.key)
