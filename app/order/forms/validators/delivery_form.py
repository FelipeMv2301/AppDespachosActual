import re
from datetime import date

from django.core.exceptions import ValidationError

from app.delivery.models.branch import Branch
from app.delivery.models.doc_type import DocumentType
from app.delivery.models.pay_type import PayType
from app.delivery.models.service import Service as DelivService
from app.delivery.models.type import Type
from app.general.models.muni import Muni
from app.general.models.service import Service
from app.general.models.service_account import ServiceAccount
from app.order.models.order import Order


class DeliveryFormValidator:
    def __init__(self, *args, **kwargs):
        self.e_msg = None

    def raise_valid_error(self):
        if self.e_msg:
            raise ValidationError(message=self.e_msg)

    def validate_order(self, value: str) -> None | ValidationError:
        splited_value = value.split(sep=',')
        for value in splited_value:
            try:
                Order.objects.filter(doc_num=value, enabled=True)
            except Order.DoesNotExist:
                self.e_msg = 'No existe(n) el/los pedido(s)'
            except Order.MultipleObjectsReturned:
                self.e_msg = 'No existe(n) pedido(s) definido(s)'

        self.raise_valid_error()

    def validate_acct(self, value: str) -> None | ValidationError:
        try:
            ServiceAccount.objects.get(code=value, enabled=True)
        except ServiceAccount.DoesNotExist:
            self.e_msg = 'No existe cuenta de servicio'
        except ServiceAccount.MultipleObjectsReturned:
            self.e_msg = 'No existe cuenta de servicio definida'

        self.raise_valid_error()

    def validate_contact_names(self, value: str) -> None | ValidationError:
        if not isinstance(value, str):
            self.e_msg = 'El valor no es texto'
        cleaned_value = re.sub(pattern=r'\W', repl='', string=value)
        if not cleaned_value:
            self.e_msg = 'El valor no es válido'

        self.raise_valid_error()

    def validate_phone_num(self, value: str) -> None | ValidationError:
        search_invalid_chars = re.findall(pattern=r'[^0-9+]+', string=value)
        search_digits = re.findall(pattern=r'[0-9]', string=value)
        search_plus_sign = re.findall(pattern=r'\+', string=value)
        if search_invalid_chars:
            self.e_msg = 'Contiene caracteres no válidos'
        elif not search_digits:
            self.e_msg = 'No contiene dígitos'
        elif not search_plus_sign:
            self.e_msg = 'No contiene signo "+"'

        self.raise_valid_error()

    def validate_addr(self, value: str) -> None | ValidationError:
        cleaned_value = re.sub(pattern=r'\W', repl='', string=value)
        if not cleaned_value:
            self.e_msg = 'El valor no es válido'

        self.raise_valid_error()

    def validate_muni(self, value: str) -> None | ValidationError:
        try:
            Muni.objects.get(code=value, enabled=True)
        except Muni.DoesNotExist:
            self.e_msg = 'No existe comuna'
        except Muni.MultipleObjectsReturned:
            raise ValidationError(
                message='No existe comuna definida')

        self.raise_valid_error()

    def validate_carrier(self, value: str) -> None | ValidationError:
        try:
            Service.objects.get(code=value, enabled=True, is_carrier=True)
        except Service.DoesNotExist:
            self.e_msg = 'No existe servicio'
        except Service.MultipleObjectsReturned:
            raise ValidationError(
                message='No existe servicio definida')

        self.raise_valid_error()

    def validate_deliv_type(self, value: str) -> None | ValidationError:
        try:
            Type.objects.get(code=value, enabled=True)
        except Type.DoesNotExist:
            self.e_msg = 'No existe tipo de engrega'
        except Type.MultipleObjectsReturned:
            raise ValidationError(
                message='No existe tipo de engrega definido')

        self.raise_valid_error()

    def validate_deliv_serv(self, value: str) -> None | ValidationError:
        try:
            DelivService.objects.get(code=value, enabled=True)
        except DelivService.DoesNotExist:
            self.e_msg = 'No existe servicio de entrega'
        except DelivService.MultipleObjectsReturned:
            raise ValidationError(
                message='No existe servicio de entrega definido')

        self.raise_valid_error()

    def validate_deliv_pay_type(self, value: str) -> None | ValidationError:
        try:
            PayType.objects.get(code=value, enabled=True)
        except PayType.DoesNotExist:
            self.e_msg = 'No existe tipo de pago'
        except PayType.MultipleObjectsReturned:
            raise ValidationError(
                message='No existe tipo de pago definido')

        self.raise_valid_error()

    def validate_branch(self, value: str) -> None | ValidationError:
        try:
            Branch.objects.get(code=value, enabled=True, delivery=True)
        except Branch.DoesNotExist:
            self.e_msg = 'No existe sucursal'
        except Branch.MultipleObjectsReturned:
            raise ValidationError(
                message='No existe sucursal definido')

        self.raise_valid_error()

    def validate_date(self, value: date) -> None | ValidationError:
        if not isinstance(value, date):
            self.e_msg = 'El tipo de valor no es válido'

        self.raise_valid_error()
