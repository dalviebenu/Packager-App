from uuid import uuid4

from utils import *


class Manifest:
    BEHAVIOR = 'data'
    RESOURCES = 'resources'
    WORLD = 'world_template'
    SKINS = 'skin_pack'

    CURRENT_FORMAT = {
        SKINS: 1,
        'default': 2
    }
    MIN_ENGINE_VERSION_KEY = 'min_engine_version'
    MIN_ENGINE_VERSION = [1, 13, 0]
    MIN_ENGINE_VERSION_TYPES = {BEHAVIOR, RESOURCES}

    def __init__(self, path_data: Path, uuid, manifest_type, version=None, name='pack.name', copy_manifest=None,
                 min_engine_version=None):
        self.uuid = uuid
        self.type = manifest_type
        self.module_uuid = uuid4()
        self.name = name
        self.version = version
        self.copy_manifest = copy_manifest or {}
        self.min_engine_version = min_engine_version
        self.path_data = path_data

    def gen_json(self):
        result = {
            "header": {
                "name": self.name,
                "version": NoIndent([1, 0, 0]),
                "uuid": str(self.uuid)
            },
            "modules": [
                {
                    "version": NoIndent([1, 0, 0]),
                    "type": str(self.type),
                    "uuid": str(self.module_uuid)
                }
            ],
            "format_version": self.CURRENT_FORMAT.get(self.type, self.CURRENT_FORMAT['default'])
        }

        deep_update(result, self.copy_manifest)

        data = load_json(self.path_data / "packager_data.json")
        descr = data["texts"]["pack.description"]

        if self.type in self.MIN_ENGINE_VERSION_TYPES:
            result['header'][self.MIN_ENGINE_VERSION_KEY] = NoIndent(self.min_engine_version)
            result['header']['description'] = descr

            if self.type == 'data':
                result['header']['name'] = (app_data["name"] + " Behavior Pack")
                result['header']['description'] = app_data["BP"]

            if self.type == 'resources':
                result['header']['name'] = (app_data["name"] + " Resource Pack")
                result['header']['description'] = app_data["RP"]

        if self.type not in self.MIN_ENGINE_VERSION_TYPES:
            if self.version is None:
                result['header']['description'] = descr
            else:
                result["header"]["version"] = NoIndent(self.version)
                result['header']['description'] = descr

        return result

    def write(self, path):
        write_json(path / 'manifest.json', self.gen_json())

    def __str__(self):
        return json.dumps(self.gen_json(), cls=MyEncoder, sort_keys=False, indent=2)

    @staticmethod
    def get_copy_manifest(path, manifest_args):
        result = {}

        manifest = load_json(path)

        for param in manifest_args:

            # Iteratively walk in the manifest using the path specified in param
            cur_manifest = manifest  # Current position in manifest
            cur_result = result  # Current position in result

            keys = param.split('/')  # Path

            for key in keys[:-1]:
                if key in cur_manifest:
                    cur_manifest = cur_manifest[key]
                    if not isinstance(cur_manifest, dict):
                        raise ManifestKeyError(path, param)

                    if key not in cur_result:
                        cur_result[key] = {}

                    cur_result = cur_result[key]

            if keys[-1] in cur_manifest:
                cur_result[keys[-1]] = cur_manifest[keys[-1]]

        return result


class PackDeclaration:
    def __init__(self, pack_uuid):
        self.uuid = pack_uuid

    def gen_json(self):
        return [
            {
                "pack_id": str(self.uuid),
                "version": [1, 0, 0]
            }
        ]

    def write(self, path):
        write_json(path, self.gen_json())


class ManifestKeyError(Exception):
    def __init__(self, path, param):
        self.path = path
        self.param = param

    def __str__(self):
        return 'Key error in manifest "{}": Invalid path "{}"'.format(self.path, self.param)
