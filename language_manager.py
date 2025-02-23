from typing import Dict
from dataclasses import dataclass
import yaml

@dataclass
class Language:
    code: str
    name: str
    native_name: str
    flag: str

class LanguageManager:
    def __init__(self