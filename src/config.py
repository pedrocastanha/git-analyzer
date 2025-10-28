import json
from pathlib import Path


class ConfigManager:
    CONFIG_FILE = '../user_config.json'

    DEFAULT_CONFIG = {
        'ai_provider': 'gemini',
        'auto_stage': True,
        'auto_push': True,
        'diff_max_size': 15000,
        'language': 'pt',
        'openai_api_key': '',
        'gemini_api_key': '',
        'gemini_model': 'gemini-2.5-flash',
        'openai_model': 'gpt-4o-mini'
    }

    def __init__(self, repo_path="."):
        self.config_path = Path(repo_path) / self.CONFIG_FILE
        self.config = self.load_config()

    def load_config(self):
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                user_config = json.load(f)
                config = self.DEFAULT_CONFIG.copy()
                config.update(user_config)
                return config
        return self.DEFAULT_CONFIG.copy()

    def save_config(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value