import uuid

from config.settings.base import logger

UNEXP_ERROR = 'Ha ocurrido un error inesperado'


class CustomError(RuntimeError):
    def __init__(self,
                 msg: str = UNEXP_ERROR,
                 log: str = None,
                 *args,
                 **kwargs):
        self.msg = msg
        self.uuid = uuid.uuid4().hex
        self.log = msg if not log else log
        logger.error(msg=f'ID:{self.uuid} {self.log}')

    def __str__(self):
        return f'{self.msg} | ID:{self.uuid}'
