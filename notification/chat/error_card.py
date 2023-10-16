from typing import Any, Dict, List

from config.settings.base import env
from notification.chat.card import Card


class ErrorCard(Card):
    def __init__(self,
                 content: List[Dict[str, Any]],
                 subtitle: str = None,
                 *args,
                 **kwargs):
        """
        Formats:
        --------
        content: [{
            'buttom_label': '',
            'content': '',
        }]
        """
        super().__init__(*args, **kwargs)
        self.content = content
        self.subtitle = subtitle
        self.template = 'error_card.json'
        self.chat_url = env.str(var='FAIL_SPACE_URL')
        self.build()

    def send_card(self, *args, **kwargs):
        self.send()
