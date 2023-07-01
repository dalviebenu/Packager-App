from utils import *


class TextsErrors:
    def __init__(self, path=None):
        self.errors = []
        self.path = path

    def add_error(self, error):
        self.errors.append(error)

    def __str__(self):
        res = ['=' * 100, '\n', 'Errors in texts directory']
        if self.path:
            res.append(' at "{}"'.format(self.path))

        res.append(':\n\n')
        for error in self.errors:
            if error.is_empty():
                continue

            res.append(str(error))
            res.append('\n')
            res.append('=' * 100)
            res.append('\n\n')

        return ''.join(res)

    def is_empty(self):
        return len(self.errors) == 0


class LangFileErrors:
    def __init__(self, name=None):
        self.errors = []
        self.name = name

    def new_key_error(self, line, key):
        self.errors.append(DuplicateKeyError(line, key))

    def new_no_equal_sign_error(self, line):
        self.errors.append(NoEqualInLineError(line))

    def __str__(self):
        if self.is_empty():  # If no errors
            res = ['# No errors in file']
            if self.name:
                res.append(' {}'.format(self.name))
            res.append('\n')
            return ''.join(res)

        res = ['# Errors in file']
        if self.name:
            res.append(' {}'.format(self.name))

        res.append(':\n')
        for error in self.errors:
            res.append('\t* {}\n'.format(error))

        return ''.join(res)

    def is_empty(self):
        return len(self.errors) == 0


class SingleLangFileError:
    def __init__(self, line):
        self.line = line


class NoEqualInLineError(SingleLangFileError):
    def __str__(self):
        return "No '=' symbol at line {}".format(self.line)


class DuplicateKeyError(SingleLangFileError):
    def __init__(self, line, key):
        super().__init__(line)
        self.key = key

    def __str__(self):
        return "Duplicate key '{}' at line {}".format(self.key, self.line)


LANGS = frozenset({
    "en_US", "de_DE", "ru_RU", "zh_CN", "fr_FR", "it_IT", "pt_BR", "fr_CA", "zh_TW", "es_MX", "es_ES", "pt_PT",
    "en_GB", "ko_KR", "ja_JP", "nl_NL", "bg_BG", "cs_CZ", "da_DK", "el_GR", "fi_FI", "hu_HU", "id_ID", "nb_NO",
    "pl_PL", "sk_SK", "sv_SE", "tr_TR", "uk_UA"
})

utf8_magic_number = '\ufeff'


class Texts:
    def __init__(self, content=None, languages=None, default_content=None, copy_langs=LANGS):
        if copy_langs is None:
            copy_langs = set()

        if languages is None:
            languages = ['en_US']

        self.content = {}

        if content is not None:
            self.content.update(content)

        for lang in languages:
            if lang not in self.content:
                self.content[lang] = LanguageFile(lang)

        if default_content is not None:
            for langfile in self.content.values():
                for key, value in default_content.items():
                    langfile[key] = value

        self.copy_langs = copy_langs

    @classmethod
    def load(cls, path, languages=None, default_content=None):
        path = Path(path)
        errors = TextsErrors(path)

        if languages is None:
            languages = []
            for p in path.glob('*.lang'):
                languages.append(p.stem)

        content = {}

        for lang in languages:
            name = lang + '.lang'
            p = path / name
            with open(p, 'r', encoding='UTF-8') as f:
                lines = f.readlines()
                if lines[0].startswith(utf8_magic_number):
                    lines[0] = lines[0][1:]

                lang_file, file_errors = LanguageFile.from_lines(lines, lang, default_content)

                # Handle file errors
                if not file_errors.is_empty():
                    file_errors.name = name
                    errors.add_error(file_errors)

                content[lang] = lang_file

        return cls(content=content, languages=languages), errors

    def write(self, path):
        path = Path(path) / 'texts'
        create(path)

        write_json(path / 'languages.json', list(self.copy_langs.union(self.languages)))

        for lang in self.languages:
            with open(path / (lang + '.lang'), 'w', encoding='UTF-8') as f:
                f.writelines(str(self.content[lang]))

        for lang in self.copy_langs:
            if lang not in self:
                with open(path / (lang + '.lang'), 'w', encoding='UTF-8') as f:
                    f.writelines(str(self.content['en_US']))

    @property
    def languages(self):
        return self.content.keys()

    def __contains__(self, item):
        return item in self.content


class SkinTexts(Texts):
    DEFAULT_ARGS = {
        'skinpack.{cap_name}': '{name}'
    }
    KEY_FORMAT = 'skin.{cap_name}.{skin_low}'

    def __init__(self, skinpack_name, *args, **kwargs):
        self.skinpack = skinpack_name
        self.skinpack_up = upper_name(self.skinpack)

        default_content = kwargs.get('default_content', {})
        default_content.update(self.get_txt_args())

        kwargs['default_content'] = default_content

        super().__init__(*args, **kwargs)

    def add_skin(self, skin):
        for langfile in self.content.values():
            langfile[self.key_str(skin)] = skin.name

    def key_str(self, skin):
        return self.KEY_FORMAT.format(cap_name=self.skinpack_up, skin_low=skin.low_name)

    def get_txt_args(self):
        fargs = {'cap_name': self.skinpack_up, 'name': self.skinpack}
        return {k.format(**fargs): v.format(**fargs) for k, v in self.DEFAULT_ARGS.items()}


class LanguageFile:
    def __init__(self, language=None, content=None):
        self.lang = language
        self.content = {}

        if content is not None:
            self.content.update(content)

    def __str__(self):
        return ''.join('{}={}\n'.format(key, value) for key, value in self.content.items())

    def write(self, path):
        with open(path) as f:
            f.write(str(self))

    @staticmethod
    def parse(lines):
        result = {}
        errors = LangFileErrors()

        for i, line in enumerate(lines, 1):
            line = line.split('#', 1)[0].strip()
            if not line:
                continue

            parts = line.split('=', 1)

            # Error handling if no = in line
            if len(parts) == 1:
                errors.new_no_equal_sign_error(i)
                continue

            key, value = parts

            # Error handling if key already present
            if key in result:
                errors.new_key_error(i, key)
                continue

            result[key] = value

        return result, errors

    @classmethod
    def from_lines(cls, lines, lang=None, default_content=None):
        content, errors = cls.parse(lines)

        res = {}
        res.update(default_content)
        res.update(content)

        return cls(lang, res), errors

    def __setitem__(self, key, value):
        self.content[key] = value

    def __getitem__(self, item):
        return self.content[item]
