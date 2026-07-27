import json
from deep_translator import GoogleTranslator
from pathlib import Path

# Path to the English source
path = Path('locales/en.json')
with open(path, 'r', encoding='utf-8') as f:
    en_data = json.load(f)

# Translate to Bulgarian
bg_data = {}
for key, value in en_data.items():
    bg_data[key] = {
        "title": GoogleTranslator(source='en', target='bg').translate(value['title']),
        "prose": GoogleTranslator(source='en', target='bg').translate(value['prose'])
    }

# Save to Bulgarian file
with open('locales/bg.json', 'w', encoding='utf-8') as f:
    json.dump(bg_data, f, ensure_ascii=False, indent=2)

print("Bulgarian translation generated at locales/bg.json")
