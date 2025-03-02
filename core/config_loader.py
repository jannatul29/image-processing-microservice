import configparser
import os
from collections import defaultdict
from typing import List

import toml
import yaml
from pydantic import BaseModel


class ConfigLoader:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        try:
            if "toml" in self.config_path:
                config_dict = self.toml_to_dict(self.config_path)
            else:
                config_dict = self.yaml_to_dict(self.config_path)
            return AppConfig(**config_dict)
        except Exception as error:
            print(error)
            return None

    @staticmethod
    def toml_to_dict(file_path):
        """Load the TOML configuration file."""
        with open(file_path, 'r', encoding="utf-8") as file:
            config_dict = toml.load(file)
        return config_dict

    @staticmethod
    def yaml_to_dict(file_path):
        """Load the YAML configuration file."""
        with open(file_path, 'r', encoding="utf-8") as file:
            config_dict = yaml.safe_load(file)
        return config_dict

    @staticmethod
    def ini_to_dict(file_path):
        """Load the INI/TOML configuration file."""
        config = configparser.ConfigParser()
        config.read(file_path)

        config_dict = defaultdict(dict)

        for section in config.sections():
            section_parts = section.split('.')
            if len(section_parts) == 1:
                config_dict[section] = dict(config.items(section))
            else:
                sub_dict = config_dict[section_parts[0]]
                for part in section_parts[1:]:
                    sub_dict = sub_dict.setdefault(part, {})
                sub_dict.update(config.items(section))

        return dict(config_dict)

    @property
    def server(self):
        """Retrieve the server config."""
        return self.config.server


    @property
    def celery(self):
        """Retrieve the celery config."""
        return self.config.celery
    
    
    @property
    def db(self):
        """Retrieve the celery config."""
        return self.config.db


    @property
    def error(self):
        """Returns the Config for Error Tracking."""
        return self.config.error


class ServerConfig(BaseModel):
    debug: bool = False
    env: str = 'development'
    allowed_hosts: List[str] = ['*']
    csrf_trusted_origins: List[str] = []
    secret_key: str = ''


class DbConfig(BaseModel):
    url: str = ''
    

class CeleryConfig(BaseModel):
    celery_result_backend: str = ''
    celery_broker_url: str = ''


class ErrorConfig(BaseModel):
    sentry_dsn: str = ''


class AppConfig(BaseModel):
    server: ServerConfig = ServerConfig()
    db: DbConfig = DbConfig()
    celery: CeleryConfig = CeleryConfig()
    error: ErrorConfig = ErrorConfig()


class DotDict(dict):
    """Dictionary with dot notation access to nested keys."""

    def __getattr__(self, item):
        try:
            value = self[item]
            if isinstance(value, dict):
                return DotDict(value)
            return value
        except KeyError as exc:
            raise AttributeError(f"Attribute {item} not found") from exc

    def __setattr__(self, key, value):
        self[key] = value


def get_config():
    CONFIG_FILE_PATH = "config/app.toml"
    if not os.path.exists(CONFIG_FILE_PATH):
        CONFIG_FILE_PATH = "config/app.conf"

    return ConfigLoader(CONFIG_FILE_PATH)
