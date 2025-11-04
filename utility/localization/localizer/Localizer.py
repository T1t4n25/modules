from __future__ import annotations
from collections import defaultdict
import json
from functools import lru_cache
from pathlib import Path
from typing import Any
import logging

# Local imports
from utility.localization.locale_context import get_locale

class Localizer:
    """
    Singleton class for managing localized messages.
    Uses pathlib for file handling and caches lookups for speed.
    """

    _instance: Localizer | None = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, main_logger: logging.Logger = None):
        if hasattr(self, "_initialized"):
            return
        if main_logger:
            self.logger = logging.getLogger(f"{main_logger.name}.Localizer")
            self.logger.setLevel(main_logger.level)
        else:
            self.logger = logging.getLogger("Localizer")
        # self.logger = logging.getLogger(f"{main_logger.na
        self._data: dict[str, dict[str, str]] = defaultdict(dict)
        self._base_path: Path = Path("utility", "localization", "locales")
        self.logger.debug("init localizer")
        self.load_all_languages()
        self._initialized = True
    # ---------------------------
    # File loading and saving
    # ---------------------------

    def load_all_languages(self) -> None:
        """Load all JSON locale files under the locales directory."""
        for file in self._base_path.glob("*.json"):
            lang = file.stem  # e.g., 'en', 'ar'
            self.logger.debug("Languages: "+lang)
            self._data[lang] = self._load_json_file(file)

    def _load_json_file(self, path: Path) -> dict[str, str]:
        """Read and parse a JSON localization file."""
        if not path.exists():
            return {}
        try:
            self.logger.debug(f"json file path {path}")
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON in {path.name}: {e}")
        except FileNotFoundError as e:
            raise RuntimeError(f"File '{path}' not found")

    def reload_language(self, lang: str) -> None:
        """Reload a single language file if it's updated."""
        file_path = self._base_path / f"{lang}.json"
        self._data[lang] = self._load_json_file(file_path)

    def save_language(self, lang: str) -> None:
        """Persist current in-memory dictionary back to its JSON file."""
        file_path = self._base_path / f"{lang}.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(self._data.get(lang, {}), f, ensure_ascii=False, indent=4)

    # ---------------------------
    # Message retrieval
    # ---------------------------


    @lru_cache(maxsize=512)
    def _cached_get_message(self, key:str, lang: str):
        """Used only with cachable calls, to not save data that will not be called again like error_id"""
        self.logger.debug("Inside _cached_get_message")
        lang = get_locale()
        msg = self._data.get(lang, {}).get(key, f"[Missing message for '{key}']")
        return msg
    
    def get_message(self, key: str, **kwargs: Any) -> str:
        """
        Retrieve a localized message by key and language.\n
        Supports string formatting placeholders (e.g., {error_id}, {field}).\n
        Any call with placeholders will not be cached, as it's variable.
        """
        msg = None
        lang = get_locale()
        self.logger.debug(f"Inside get_message with lang: {lang}")
        if not kwargs:
            msg = self._cached_get_message(key=key, lang=lang)
        else:
            self.logger.debug("Inside get_message")
            msg = self._data.get(lang, {}).get(key, f"[Missing message for '{key}']")
            
        # pprint(self._data)
        return msg.format(**kwargs) if kwargs else msg


if __name__ == "__main__":
    import sys
    sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
    from pprint import pprint
    from localization.locale_context import get_locale
    from localization.messages import PRODUCT_NOT_FOUND
    pprint(Path(__file__).resolve().parent)
    localizer = Localizer()
    pprint(localizer.get_message(key=PRODUCT_NOT_FOUND.message_key))