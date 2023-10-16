import uuid

from config.settings.base import logger
from notification.chat.error_card import ErrorCard

UNEXP_ERROR = 'Ha ocurrido un error inesperado'


class CustomError(RuntimeError):
    def __init__(self,
                 msg: str = UNEXP_ERROR,
                 log: str = None,
                 notify: bool = False,
                 *args,
                 **kwargs):
        self.msg = msg
        self.uuid = uuid.uuid4().hex
        self.log = msg if not log else log
        logger.error(msg=f'ID:{self.uuid} {self.log}')

        if notify:
            content = [
                {
                    'buttom_label': 'Error',
                    'content': str(self.msg)
                },
                {
                    'buttom_label': 'ID',
                    'content': str(self.uuid)
                }
            ]
            card = ErrorCard(content=content)
            card.send_card()

    def __str__(self):
        return f'{self.msg} | ID:{self.uuid}'
