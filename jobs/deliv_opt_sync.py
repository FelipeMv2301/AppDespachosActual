from django.contrib.auth.models import User
from simple_history.utils import bulk_create_with_history

from app.delivery.models.branch import Branch
from app.delivery.models.opt import Option
from app.delivery.models.pay_type import PayType
from app.delivery.models.service import Service as DelivService
from app.delivery.models.type import Type
from app.general.models.service import Service
from core.settings.base import APP_USERNAME

user = User.objects.get(username=APP_USERNAME)

carriers = {o.code: o
            for o in Service.objects.filter(is_carrier=True)}
branches = {o.code: o
            for o in Branch.objects.all()}
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
                for branch_code, branch in branches.items():
                    branch_carrier = branch.service_acct.service

                    if type_code == 'HOMEDELIV':  # A domicilio
                        continue
                    elif branch_carrier.code != carrier_code:
                        continue
                    elif carrier_code == 'STK' and pay_type_code == 'FREE':
                        continue

                    opt = Option.objects.filter(
                        carrier=branch_carrier,
                        service=service,
                        type=_type,
                        pay_type=pay_type,
                        branch=branch
                    )
                    if opt:
                        continue
                    opt = Option()
                    opt.carrier = branch_carrier
                    opt.service = service
                    opt.type = _type
                    opt.pay_type = pay_type
                    opt.branch = branch
                    opt.changed_by = user
                    opt.enabled = type_code == 'BRDELIV'  # Retiro en sucursal
                    bulk_create_with_history(
                        objs=[opt],
                        model=Option
                    )

                if type_code == 'BRDELIV':  # Retiro en sucursal
                    continue
                elif carrier_code == 'STK' and pay_type_code == 'FREE':
                    continue

                opt = Option.objects.filter(
                    carrier=carrier,
                    service=service,
                    type=_type,
                    pay_type=pay_type,
                    branch=None
                )
                if opt:
                    continue
                opt = Option()
                opt.carrier = carrier
                opt.service = service
                opt.type = _type
                opt.pay_type = pay_type
                opt.changed_by = user
                opt.enabled = type_code == 'HOMEDELIV'  # A domicilio
                bulk_create_with_history(
                    objs=[opt],
                    model=Option
                )
