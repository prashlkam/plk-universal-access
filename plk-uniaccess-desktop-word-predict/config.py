import json, os
class Config:
    def __init__(self, path=None):
        self.path = path or (os.path.join(os.path.expanduser('~'), '.wordq_config.json'))
    def load(self):
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    def save(self, data):
        try:
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print('Failed to save config:', e)
