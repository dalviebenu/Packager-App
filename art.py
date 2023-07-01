from typing import Iterable
from images import Image
from utils import *


class StoreArt:
    thumbnail_name = '{up_name}_Thumbnail_0.jpg'
    icon_name = '{up_name}_packicon_0.jpg'
    panorama_name = '{up_name}_Panorama_0.jpg'
    screenshot_name = '{up_name}_Screenshot_{i}.jpg'

    def __init__(self, thumbnail: Image, icon: Image, panorama: Image, screenshots: Iterable[Image], fargs):
        self.thumbnail = thumbnail
        self.pack_icon = icon
        self.screenshots = list(screenshots) if screenshots is not None else []

        self.panorama = panorama

        self.fargs = fargs

    @classmethod
    def load(cls, path, world, fargs):
        path = Path(path)

        thumbnail = Image(path / 'S0.jpg', MEDIUM)
        screenshots = (Image(path / 'S{}.jpg'.format(i), MEDIUM) for i in range(1, 11)) if world else None
        panorama = Image(path / 'pano.jpg', PANORAMA) if world else None
        icon = Image(path / 'S11.jpg', L_SQ) if world and (path / 'S11.jpg').is_file() else None

        return cls(thumbnail, icon, panorama, screenshots, fargs)

    def write(self, path: Path):
        path = path / 'Store Art'
        create(path)

        self.thumbnail.write(path / self.thumbnail_name.format(**self.fargs))
        if self.pack_icon:
            self.pack_icon.write(path / self.icon_name.format(**self.fargs))
        if self.panorama:
            self.panorama.write(path / self.panorama_name.format(**self.fargs))

        if self.screenshots:
            for i, img in enumerate(self.screenshots):
                img.write(path / self.screenshot_name.format(i=i, **self.fargs))


class MarketingArt:
    key_art_name = '{up_name}_MarketingKeyArt.jpg'
    screenshot_name = '{up_name}_Screenshot_{i}.jpg'
    partner_art_name = '{up_name}_PartnerArt.jpg'

    def __init__(self, key_art: Image, screenshots: Iterable[Image], partner_art: Image, fargs):
        self.key_art = key_art
        self.screenshots = list(screenshots) if screenshots is not None else []
        self.partner_art = partner_art
        self.fargs = fargs

    @classmethod
    def load(cls, path: Path, world, fargs):
        key_art = Image(path / 'M0.jpg', HD)
        screenshots = (Image(path / 'M{}.jpg'.format(i), HD) for i in range(1, 11)) if world else None
        partner_art = Image(path / 'banner.jpg', HD)

        return cls(key_art, screenshots, partner_art, fargs)

    def write(self, path: Path):
        path = path / 'Marketing Art'
        create(path)

        self.key_art.write(path / self.key_art_name.format(**self.fargs))
        if self.screenshots:
            for i, img in enumerate(self.screenshots):
                img.write(path / self.screenshot_name.format(i=i, **self.fargs))

        self.partner_art.write(path / self.partner_art_name.format(**self.fargs))
