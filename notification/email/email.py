import base64
import os
from pathlib import Path
from typing import Dict, List, Sequence

from django.core.mail import EmailMessage

CURRENT_PATH = Path(__file__).resolve().parent
NOTIFICATON_PATH = CURRENT_PATH.parent
ATTACHMENTS_PATH = os.path.join(NOTIFICATON_PATH, 'attachments')


class Email(EmailMessage):
    def __init__(self,
                 to: Sequence[str],
                 subject: str,
                 from_email: str | None = None,
                 body: str = None,
                 body_content_type: str = 'html',
                 cc: Sequence[str] = None,
                 bcc: Sequence[str] = None,
                 reply_to: Sequence[str] = None,
                 attachments: List[Dict[str, str | bytes]] = [],
                 *args,
                 **kwargs):
        super().__init__(subject=subject,
                         from_email=from_email,
                         to=to,
                         body=body,
                         cc=cc,
                         bcc=bcc,
                         reply_to=reply_to,
                         *args,
                         **kwargs)
        self.content_subtype = body_content_type
        self.attachs = attachments
        for attachment in self.attachs:
            filepath = attachment.get('filepath')
            filename = (attachment.get('filename') or
                        os.path.basename(filepath))
            content = attachment.get('content')
            self.attach(filename=filename,
                        content=content,
                        mimetype=attachment.get('mime_type'))
            content_b64 = base64.b64encode(s=content)
            b64_string = content_b64.decode(encoding='utf-8')
            attachment['content'] = b64_string

    def send(self, *args, **kwargs):
        super().send(*args, **kwargs)
