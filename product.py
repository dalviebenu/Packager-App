from art import *
from skinpack import *
from world import *


class Content:
    SKIN_PACK_NAME = '{name} Skin Pack'

    def __init__(self, store_art, marketing_art, name, skin_pack=None, world=None, full_name=None,
                 skin_pack_name=None):
        self.store_art = store_art
        self.marketing_art = marketing_art
        self.skin_pack = skin_pack
        self.world = world
        self.name = name
        self.full_name = full_name or self.name
        self.skin_pack_name = skin_pack_name or self.SKIN_PACK_NAME.format(self.name)

        if not (self.skin_pack or self.world):
            raise NoContentError()

    @classmethod
    def load(cls, path, name=None, uuid_w=None, uuid_s=None, version=None, min_engine_version=None, languages=None,
             full_name=None, skin_pack_name=None):
        path = Path(path)
        if name is None:
            name = path.name  # name of the folder (pre_furniture)

        w = None
        world_path = path / 'world'
        if world_path.is_dir():
            worlds = list(filter(is_world, world_path.iterdir()))
            # returns the folder where there is a text file named levelname.txt
            # print (worlds) # path with CAMM... (folder in world folder)

            if len(worlds) > 1:
                raise MultipleWorldsError(world_path)
                # More than one item in worlds.

            if len(worlds) == 1:
                w = worlds[0] # path of world/CAMM file.
                if full_name is None:
                    with open(w / 'levelname.txt', 'r', encoding='UTF-8') as f:
                        full_name = f.readline()

        fargs = FormattingArgs(name=name, full_name=full_name) # dict of formatted names.

        if skin_pack_name is None:
            skin_pack_name = cls.SKIN_PACK_NAME.format(**fargs)
            # formats SKIN_PACK_NAME with fargs. (dict of names)

        art_path = path / 'Art'
        if not art_path.is_dir():
            raise NoArtError(art_path)

        store_art = StoreArt.load(art_path, w, fargs)
        marketing_art = MarketingArt.load(art_path, w, fargs)

        # World Template
        world = None
        if w:
            txt_args = {
                'pack.name': full_name
            }

            world = World.load(w, store_art.thumbnail, store_art.pack_icon, fargs, uuid_w=uuid_w, version=version,
                               min_engine_version=min_engine_version, languages=languages, txt_args=txt_args)

        # Skin Pack
        skin_pack = None
        skin_path = path / 'Skins'
        if skin_path.is_dir():
            skin_pack = SkinPack.load(skin_path, skin_pack_name, uuid_s, languages)

        try:
            return cls(store_art, marketing_art, name, skin_pack, world, full_name, skin_pack_name)
        except NoContentError:
            raise NoContentError(path)

    def write(self, path):
        path = Path(path)
        create(path)

        self.store_art.write(path)
        self.marketing_art.write(path)

        content_path = path / 'Content'

        if self.world:
            self.world.write(content_path)

        if self.skin_pack:
            self.skin_pack.write(content_path)


class NoContentError(Exception):
    def __init__(self, path=None):
        self.path = path

    def __str__(self):
        msg = 'No world and no skin pack found'
        if self.path:
            msg += ' at "{}"'.format(self.path)

        return msg


class NoArtError(Exception):
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return 'No art folder found at "{}"'.format(self.path)


class MultipleWorldsError(Exception):
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return 'Multiple worlds found in "{}"'.format(self.path)
