import yaml
import sys

from src.utils import logger
from src.config import config
from src.lang.language_models import Model

class AutoFormatStr(str):
    def __call__(self):
        frame = sys._getframe(1)
        context = {**frame.f_globals, **frame.f_locals}
        return self.format(**context)

class LanguageObject:
    def __init__(self, dictionary: dict):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                setattr(self, key, LanguageObject(value))
            elif isinstance(value, str):
                setattr(self, key, AutoFormatStr(value))
            else:
                setattr(self, key, value)

def load_language(lang_code):
    path = f"src/data/locales/{lang_code}.yaml"

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
            return LanguageObject(data)
    except Exception as e:
        logger(f"Failed loading language file: {e}", "FATAL")

lang: Model = load_language(config.discord.lang)