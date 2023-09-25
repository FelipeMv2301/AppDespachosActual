import json
import traceback
from typing import Any, Dict

import pandas as pd
import requests
from django.contrib.auth.models import User
from simple_history.utils import (bulk_create_with_history,
                                  bulk_update_with_history)

from app.delivery.models.account import Account
from app.delivery.models.delivery import Delivery as DelivMdl
from app.delivery.models.status_third import StatusThird
from app.delivery.models.status import Status
from classes.starken.starken import Starken
from core.settings.base import APP_USERNAME
from helpers.decorator.loggable import loggable
from helpers.error.custom_error import UNEXP_ERROR, CustomError


class Delivery(Starken):
    def __init__(self,
                 account: Account = None,
                 folio: int = None,
                 *args,
                 **kwargs):
        super().__init__(account=account, *args, **kwargs)

        self.folio = folio

    @loggable
    def track_by_folio(self, *args, **kwargs) -> Dict[str, Any]:
        url = self.trk_api_path.format(folio=self.folio)
        response = requests.get(url=url, headers=self.api_headers)
        self.check_response(response=response)

        return json.loads(s=response.text)

    @loggable
    def app_sync(self, *args, **kwargs):
        mdl = DelivMdl
        status_mdl = StatusThird
        user_obj = User.objects.get(username=APP_USERNAME)
        carrier = self.account.carrier

        delivs = mdl.objects.filter(account=self.account)
        status = {st.code: st
                  for st in status_mdl.objects.filter(carrier=carrier)}
        for deliv in delivs:
            self.folio = deliv.folio
            try:
                tracking = self.track_by_folio()
            except CustomError:
                print(f'Folio: {self.folio}')
                continue
            except Exception:
                tb = traceback.format_exc()
                tb += f'Folio: {self.folio}'
                e_msg = f'{UNEXP_ERROR}\nFolio: {self.folio}'
                CustomError(msg=e_msg, log=tb)
                continue

            try:
                status_id = str(tracking['status_id'])
                status_desc = tracking['status_op']
                update_date = (pd.to_datetime(arg=tracking['updated_at'])
                               .to_pydatetime())

            except KeyError:
                tb = traceback.format_exc()
                tb += f'Folio: {self.folio}'
                e_msg = f'Error: {UNEXP_ERROR}'
                e_msg += f'\nFolio: {self.folio}'
                CustomError(msg=e_msg, log=tb)
                continue
            try:
                status_obj = status[status_id]
                status_name = status_obj.name
                if status_desc != status_name:
                    status_obj.name = status_desc
                    status_obj.changed_by = user_obj
                    try:
                        bulk_update_with_history(objs=[status_obj],
                                                 model=status_mdl,
                                                 fields=['name', 'changed_by'])
                    except Exception:
                        tb = traceback.format_exc()
                        tb += f'Folio: {self.folio}'
                        e_msg = f'Error: {UNEXP_ERROR}'
                        e_msg += f'\nFolio: {self.folio}'
                        CustomError(msg=e_msg, log=tb)
                        continue
            except KeyError:
                status_obj = status_mdl(
                    code=status_id,
                    name=status_desc,
                    carrier=carrier,
                    changed_by=user_obj
                )
                try:
                    status_obj = bulk_create_with_history(objs=[status_obj],
                                                          model=status_mdl)[0]
                except Exception:
                    tb = traceback.format_exc()
                    tb += f'Folio: {self.folio}'
                    e_msg = f'Error: {UNEXP_ERROR}'
                    e_msg += f'\nFolio: {self.folio}'
                    CustomError(msg=e_msg, log=tb)
                    continue
                status[status_id] = status_obj

            fields_to_upd = ['third_status', 'changed_by']
            if status_obj.status:
                deliv.status = status_obj.status
                fields_to_upd.append('status')
                if status_obj.status.code == Status.receiv_code:
                    deliv.rcpt_date = update_date
                    fields_to_upd.append('rcpt_date')
            deliv.third_status = status_desc
            deliv.changed_by = user_obj
            try:
                bulk_update_with_history(objs=[deliv],
                                         model=mdl,
                                         fields=fields_to_upd)
            except Exception:
                tb = traceback.format_exc()
                tb += f'Folio: {self.folio}'
                e_msg = f'Error: {UNEXP_ERROR}'
                e_msg += f'\nFolio: {self.folio}'
                CustomError(msg=e_msg, log=tb)
                continue
