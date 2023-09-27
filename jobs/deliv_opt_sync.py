from django.contrib.auth.models import User
from simple_history.utils import bulk_create_with_history

from app.delivery.models.agency import Agency
from app.delivery.models.opt import Option
from app.delivery.models.pay_type import PayType
from app.delivery.models.service import Service as DelivService
from app.delivery.models.type import Type
from app.general.models.service import Service
from core.settings.base import APP_USERNAME

user = User.objects.get(username=APP_USERNAME)

carriers = {o.code: o
            for o in Service.objects.filter(is_carrier=True)}
agencies = {o.code: o
            for o in Agency.objects.all()}
pay_types = {o.code: o
             for o in PayType.objects.all()}
services = {o.code: o
            for o in DelivService.objects.all()}
types = {o.code: o
         for o in Type.objects.all()}

for carrier_code, carrier in carriers.items():
    for pay_type_code, pay_type in pay_types.items():
        for service_code, service in services.items():
            for type_code, _type in types.items():
                for ag_code, ag in agencies.items():
                    ag_carrier = ag.service_acct.service
                    opt = Option.objects.filter(
                        carrier=ag_carrier,
                        service=service,
                        type=_type,
                        pay_type=pay_type,
                        agency=ag
                    )
                    if opt:
                        continue
                    opt = Option()
                    opt.carrier = ag_carrier
                    opt.service = service
                    opt.type = _type
                    opt.pay_type = pay_type
                    opt.agency = ag
                    opt.changed_by = user
                    opt.enabled = type_code == 'RAG'
                    bulk_create_with_history(
                        objs=[opt],
                        model=Option
                    )
                opt = Option.objects.filter(
                    carrier=carrier,
                    service=service,
                    type=_type,
                    pay_type=pay_type,
                    agency=None
                )
                if opt:
                    continue
                opt = Option()
                opt.carrier = carrier
                opt.service = service
                opt.type = _type
                opt.pay_type = pay_type
                opt.changed_by = user
                match carrier_code:
                    case 'BQ':
                        enabled = type_code != 'RAG'
                    case 'STK':
                        enabled = type_code != 'RBQ'
                    case _:
                        enabled = True
                opt.enabled = enabled
                bulk_create_with_history(
                    objs=[opt],
                    model=Option
                )
