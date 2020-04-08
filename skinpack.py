from uuid import uuid4
from images import Image
from manifest import Manifest
from texts import SkinTexts
from utils import *
import numpy as np
from PIL import Image as PILImage


class SkinPack:
    def __init__(self, skins, name, cap_name, uuid_s, texts):
        if uuid_s is None:
            self.uuid = uuid4()
        else:
            self.uuid = uuid_s

        self.skins = skins
        self.texts = texts

        self.name = name
        self.cap_name = cap_name

        self.manifest = Manifest(self.uuid, Manifest.SKINS, name=self.cap_name)

    @classmethod
    def load(cls, path, name, uuid_s=None, languages=None):
        path = Path(path)

        if languages is None:
            languages = ['en_US']

        cap_name = upper_name(name)

        skins = []
        texts = SkinTexts(name, languages=languages, copy_langs=None)
        for p in path.glob('*.png'):
            skin_name = p.stem
            img = Image(p, ANY)

            skin = Skin(skin_name, img)

            texts.add_skin(skin)
            skins.append(skin)

        return cls(skins, name, cap_name, uuid_s, texts)

    def get_json(self):
        return {
            'skins': [
                skin.gen_json() for skin in self.skins
            ],
            'serialize_name': self.cap_name,
            'localization_name': self.cap_name

        }

    def write(self, path):
        path = Path(path) / 'skin_pack'
        create(path)

        for skin in self.skins:
            skin.write(path)

        write_json(path / 'skins.json', self.get_json())

        self.texts.write(path)
        self.manifest.write(path)


class Skin:
    PAID = 'paid'
    FREE = 'free'

    STEVE = 0
    ALEX = 1

    geom = {
        STEVE: 'geometry.humanoid.custom',
        ALEX: 'geometry.humanoid.customSlim'
    }

    name_regex = re.compile('^(?P<name>.*?)(?P<free>_free)?(?P<model>_[mf])?$', re.IGNORECASE)

    HD = True
    LD = False
    HD_FORMAT = (128, 128)
    LD_FORMAT = (64, 64)

    skin_templates = src_dir / 'Skin Templates'
    STEVE_TEMPLATE = PILImage.open(skin_templates / 'steve.png')
    ALEX_TEMPLATE = PILImage.open(skin_templates / 'alex.png')
    HD_STEVE_TEMPLATE = STEVE_TEMPLATE.resize(HD_FORMAT, PILImage.NEAREST)
    HD_ALEX_TEMPLATE = ALEX_TEMPLATE.resize(HD_FORMAT, PILImage.NEAREST)

    templates = {
        STEVE: {
            HD: HD_STEVE_TEMPLATE,
            LD: STEVE_TEMPLATE
        },
        ALEX: {
            HD: HD_ALEX_TEMPLATE,
            LD: ALEX_TEMPLATE
        }
    }

    @staticmethod
    def normalize_name(name):
        return name.replace('_', ' ').strip()

    def __init__(self, name, texture):
        match = self.name_regex.match(name)
        groups = match.groupdict()

        self.name = self.normalize_name(groups['name'])
        self.low_name = skin_lower(name)

        self.type = self.FREE if groups['free'] else self.PAID

        self.texture = texture
        self.definition = self.texture.img.size == self.HD_FORMAT
        self.model = self.ALEX if (groups['model'] is not None and groups['model'].lower() == '_f') else self.STEVE

        self.check_validity()

    def gen_json(self):
        return {
            'localization_name': self.low_name,
            'geometry': self.geom[self.model],
            'texture': '{}.png'.format(self.low_name),
            'type': self.type
        }

    def write(self, path):
        path = Path(path)
        self.texture.write(path / '{}.png'.format(self.low_name))

    def check_validity(self):
        pixels = get_pixel_matrix(self.texture.img)

        template = get_pixel_matrix(self.templates[self.model][self.definition])
        for color in np.unique(template):
            if color == 0:
                continue
            mask = template == color
            if pixels[mask][0] != 0 and np.all(pixels[mask] == pixels[mask][0]):
                pos = np.where(mask)
                print('Error detected in skin "{}": Same color from {} to {}, in (x, y) format'.format(
                    self.name, (pos[0][0], pos[1][0]), (pos[0][-1], pos[1][-1])))
