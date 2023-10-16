import json
import os
from pathlib import Path

import requests

CURRENT_PATH = Path(__file__).resolve().parent
NOTIFICATON_PATH = CURRENT_PATH.parent
TEMPLATES_PATH = os.path.join(NOTIFICATON_PATH, 'templates')


class Card:
    def __init__(self, *args, **kwargs):
        self.content = None
        self.card = None
        self.template = None
        self.subtitle = None
        self.chat_url = None

    def build(self, *args, **kwargs):
        try:
            filepath = os.path.join(TEMPLATES_PATH, self.template)
            file = open(file=filepath,
                        mode='r',
                        encoding='utf-8',
                        errors='ignore')
            body = json.load(fp=file)
            data = body['cards'][0]
            widgets = data['sections'][0]['widgets']

            if self.subtitle:
                data['header']['subtitle'] = str(self.subtitle)

            for i, elem in enumerate(self.content):
                if i >= len(widgets):
                    widgets.append({
                        'keyValue': {
                            'bottomLabel': '',
                            'content': ''
                        }
                    })
                widget_key_value = widgets[i]['keyValue']
                widget_key_value['bottomLabel'] = str(elem['buttom_label'])
                widget_key_value['content'] = str(elem['content'])

            self.card = body

        except Exception:
            pass

    def send(self, *args, **kwargs):
        requests.post(
            url=self.chat_url,
            data=json.dumps(obj=self.card),
            headers={'Content-Type': 'application/json'}
        )
