from datetime import datetime
from typing import Any, Mapping

from django import forms
from django.core.validators import EmailValidator

from app.delivery.forms.validators.issue import IssueValidator
from app.delivery.models.branch import Branch
from app.delivery.models.doc_type import DocumentType
from app.delivery.models.pay_type import PayType
from app.delivery.models.service import Service as DelivServ
from app.delivery.models.type import Type
from app.general.models.muni import Muni
from app.general.models.service import Service
from app.general.models.service_account import ServiceAccount


class IssueForm(forms.Form):
    orders = forms.CharField(
        label='Pedido(s)',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'mb-2 textfield search-bar',
                'aria-controls': 'myResults',
                'placeholder': '2307482',
                'autocomplete': 'off',
            }
        )
    )
    group = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'hidden': 'true'}),
        validators=[IssueValidator().validate_group],
        max_length=100,
    )
    acct = forms.ChoiceField(
        label='Cuenta de servicio',
        required=True,
        disabled=False,
        choices=((sa.code, f'{sa.name} - {sa.desc}')
                 for sa in (ServiceAccount.objects.filter(enabled=True)
                            .order_by('name'))),
        widget=forms.Select(
            attrs={
                'class': 'mb-2 textfield',
            }
        ),
        validators=[IssueValidator().validate_acct],
    )
    contact_first_name = forms.CharField(
        label='Nombre de contacto',
        max_length=100,
        required=True,
        disabled=False,
        widget=forms.TextInput(
            attrs={
                'class': 'mb-2 textfield',
                'maxlength': '100',
                'oninput': 'this.value = this.value.slice(0, 100);',
            }
        ),
        validators=[IssueValidator().validate_contact_names],
    )
    contact_last_name = forms.CharField(
        label='Apellido de contacto',
        max_length=100,
        required=True,
        disabled=False,
        widget=forms.TextInput(
            attrs={
                'class': 'mb-2 textfield',
                'maxlength': '100',
                'oninput': 'this.value = this.value.slice(0, 100);',
            }
        ),
        validators=[IssueValidator().validate_contact_names],
    )
    contact_email_addr = forms.EmailField(
        label='Correo electrónico de contacto',
        max_length=100,
        required=True,
        disabled=False,
        widget=forms.EmailInput(
            attrs={
                'class': 'mb-2 textfield',
                'placeholder': 'correo@dominio.com',
                'maxlength': '100',
                'oninput': 'this.value = this.value.slice(0, 100);',
            }
        ),
        validators=[EmailValidator],
    )
    contact_phone1 = forms.CharField(
        label='Teléfono 1 de contacto',
        max_length=100,
        required=False,
        disabled=False,
        widget=forms.TextInput(
            attrs={
                'class': 'mb-2 textfield',
                'oninput': ('this.value = this.value.replace(/[^0-9+]+/g, "");'
                            'this.value = this.value.slice(0, 100);'),
                'placeholder': '+56253093750',
                'maxlength': '100',
            }
        ),
        validators=[IssueValidator().validate_phone_num],
    )
    contact_phone2 = forms.CharField(
        label='Teléfono 2 de contacto',
        max_length=100,
        required=False,
        disabled=False,
        widget=forms.TextInput(
            attrs={
                'class': 'mb-2 textfield',
                'oninput': ('this.value = this.value.replace(/[^0-9+]+/g, "");',
                            'this.value = this.value.slice(0, 100);'),
                'placeholder': '+56253093750',
                'maxlength': '100',
            }
        ),
        validators=[IssueValidator().validate_phone_num],
    )
    contact_mobile_phone = forms.CharField(
        label='Teléfono de contacto',
        max_length=100,
        required=False,
        disabled=False,
        widget=forms.TextInput(
            attrs={
                'class': 'mb-2 textfield',
                'placeholder': '+56934739440',
                'maxlength': '100',
                'oninput': ('this.value = this.value.replace(/[^0-9+]+/g, "");',
                            'this.value = this.value.slice(0, 100);'),
            }
        ),
        validators=[IssueValidator().validate_phone_num],
    )
    deliv_st_and_num = forms.CharField(
        label='Calle y numeración de entrega',
        max_length=100,
        required=True,
        disabled=False,
        widget=forms.TextInput(
            attrs={
                'class': 'mb-2 textfield',
                'placeholder': 'Calle y número',
                'maxlength': '100',
                'oninput': 'this.value = this.value.slice(0, 100);',
            }
        ),
        validators=[IssueValidator().validate_addr],
    )
    deliv_addr_complement = forms.CharField(
        label='Complemento de dirección',
        max_length=100,
        required=True,
        disabled=False,
        widget=forms.TextInput(
            attrs={
                'class': 'mb-2 textfield',
                'placeholder': 'Of/Dpto/Block/Casa',
                'maxlength': '100',
                'oninput': 'this.value = this.value.slice(0, 100);',
            }
        ),
        validators=[IssueValidator().validate_addr],
    )
    deliv_muni = forms.ChoiceField(
        label='Comuna de entrega',
        required=True,
        disabled=False,
        choices=((m.code, m.name)
                 for m in (Muni.objects.filter(enabled=True)
                           .order_by('name'))),
        widget=forms.Select(
            attrs={
                'class': 'mb-2 textfield',
                'onchange': 'searchDeliveryOption()',
            }
        ),
        validators=[IssueValidator().validate_muni],
    )
    carrier = forms.ChoiceField(
        label='Vía de entrega',
        required=True,
        disabled=False,
        choices=((s.code, s.name)
                 for s in (Service.objects
                           .filter(enabled=True, is_carrier=True)
                           .order_by('name'))),
        widget=forms.Select(
            attrs={
                'class': 'mb-2 textfield',
                'onchange': 'searchDeliveryOption(); requiredFieldsManage(this.value);',
            }
        ),
        validators=[IssueValidator().validate_service],
    )
    is_complete = forms.ChoiceField(
        label='¿Envío completo?',
        required=True,
        disabled=False,
        initial='Y',
        choices=(('Y', 'Sí'), ('N', 'No')),
        widget=forms.Select(
            attrs={
                'class': 'mb-2 textfield',
            }
        ),
    )
    deliv_type = forms.ChoiceField(
        label='Tipo de entrega',
        required=True,
        disabled=False,
        choices=((t.code, t.name)
                 for t in (Type.objects.order_by('name'))),
        widget=forms.Select(
            attrs={
                'class': 'mb-2 textfield',
                'onchange': 'searchDeliveryOption()',
            }
        ),
        validators=[IssueValidator().validate_deliv_type],
    )
    deliv_service = forms.ChoiceField(
        label='Tipo de servicio',
        required=True,
        disabled=False,
        choices=((s.code, s.name)
                 for s in (DelivServ.objects.order_by('name'))),
        widget=forms.Select(
            attrs={
                'class': 'mb-2 textfield',
                'onchange': 'searchDeliveryOption()',
            }
        ),
        validators=[IssueValidator().validate_deliv_serv],
    )
    deliv_pay_type = forms.ChoiceField(
        label='Tipo de pago de entrega',
        required=True,
        disabled=False,
        choices=((p.code, p.name)
                 for p in (PayType.objects.order_by('name'))),
        widget=forms.Select(
            attrs={
                'class': 'mb-2 textfield',
                'onchange': 'searchDeliveryOption()',
            }
        ),
        validators=[IssueValidator().validate_deliv_pay_type],
    )
    branch = forms.ChoiceField(
        label='Sucursal de entrega',
        required=False,
        disabled=False,
        choices=((b.code, b.name)
                 for b in (Branch.objects.order_by('name'))),
        widget=forms.Select(
            attrs={
                'class': 'mb-2 textfield',
            }
        ),
        validators=[IssueValidator().validate_branch],
    )
    obs = forms.CharField(
        label='Observaciones de entrega',
        max_length=255,
        required=False,
        disabled=False,
        widget=forms.TextInput(
            attrs={
                'class': 'mb-2 textfield',
                'maxlength': '255',
                'oninput': 'this.value = this.value.slice(0, 255);',
            }
        )
    )
    assy_date = forms.DateField(
        label='Fecha de armado',
        required=True,
        disabled=False,
        initial=datetime.now().strftime('%Y-%m-%d'),
        widget=forms.DateInput(
            attrs={
                'class': 'mb-2 textfield',
                'type': 'date',
            }
        ),
        validators=[IssueValidator().validate_date],
    )
    height = forms.FloatField(
        label='Alto',
        required=True,
        disabled=False,
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                'class': 'textfield mb-2',
                'style': 'padding-right: 2rem;',
                'onchange': 'this.value = this.value.replace(/[^0-9.]*/g, "");',
                'min': '1',
                'step': '0.01',
                'placeholder': '12.8',
            }
        ),
        validators=[IssueValidator().validate_int_or_float],
    )
    width = forms.FloatField(
        label='Ancho',
        required=True,
        disabled=False,
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                'class': 'textfield mb-2',
                'style': 'padding-right: 2rem;',
                'onchange': 'this.value = this.value.replace(/[^0-9.]*/g, "");',
                'min': '1',
                'step': '0.01',
                'placeholder': '5.3',
            }
        ),
        validators=[IssueValidator().validate_int_or_float],
    )
    length = forms.FloatField(
        label='Largo',
        required=True,
        disabled=False,
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                'class': 'textfield mb-2',
                'style': 'padding-right: 2rem;',
                'onchange': 'this.value = this.value.replace(/[^0-9.]*/g, "");',
                'min': '1',
                'step': '0.01',
                'placeholder': '8.2',
            }
        ),
        validators=[IssueValidator().validate_int_or_float],
    )
    volume = forms.FloatField(
        label='Volumen',
        required=False,
        disabled=False,
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                'class': 'textfield mb-2',
                'style': 'padding-right: 2.5rem;',
                'onchange': 'this.value = this.value.replace(/[^0-9.]*/g, "");',
                'min': '1',
                'step': '0.01',
                'placeholder': '45.3',
            }
        )
    )
    weight = forms.FloatField(
        label='Peso',
        required=True,
        disabled=False,
        min_value=1,
        max_value=9999,
        widget=forms.NumberInput(
            attrs={
                'maxlength': '4',
                'minlength': '1',
                'class': 'textfield mb-2',
                'style': 'padding-right: 2rem;',
                'oninput': ('this.value = this.value.replace(/[^0-9.]*/g, "");'
                            'this.value = this.value.slice(0,4);'),
                'min': '1',
                'max': '9999',
                'step': '0.01',
                'placeholder': '9.8',
            }
        ),
        validators=[IssueValidator().validate_int_or_float],
    )
    pack_qty = forms.IntegerField(
        label='Cant bultos',
        required=True,
        disabled=False,
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                'class': 'textfield mb-2',
                'step': '1',
                'onchange': 'this.value = this.value.replace(/[^0-9]*/g, "");',
                'min': '1',
                'placeholder': '2',
            }
        ),
        validators=[IssueValidator().validate_int_or_float],
    )
    valuation = forms.IntegerField(
        label='Valoración',
        required=True,
        disabled=False,
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                'class': 'textfield mb-2',
                'style': 'padding-right: 1.5rem;',
                'step': '1',
                'onchange': 'this.value = this.value.replace(/[^0-9]*/g, "");',
                'min': '1',
                'placeholder': '150990',
            }
        ),
        validators=[IssueValidator().validate_int_or_float],
    )
    doc_folio = forms.IntegerField(
        label='Folio del documento',
        min_value=1,
        required=True,
        widget=forms.NumberInput(
            attrs={
                'class': 'textfield mb-2',
                'onchange': 'this.value = this.value.replace(/[^0-9]*/g, "");',
                'min': '1',
            }
        ),
        validators=[IssueValidator().validate_int_or_float],
    )
    doc_type = forms.ChoiceField(
        label='Tipo del documento',
        required=True,
        choices=((dt.code, dt.name)
                 for dt in (DocumentType.objects
                            .filter(enabled=True)
                            .order_by('name'))),
        widget=forms.Select(
            attrs={
                'class': 'textfield mb-2'
            }
        ),
        validators=[IssueValidator().validate_doc_type],
    )

    def __init__(self, data: Mapping[str, Any] = None, *args, **kwargs):
        super().__init__(data=data, *args, **kwargs)
        if data:
            if data.get('carrier') != 'STK':
                self.fields['height'].required = False
                self.fields['width'].required = False
                self.fields['length'].required = False
                self.fields['weight'].required = False
                self.fields['pack_qty'].required = False
                self.fields['valuation'].required = False
                self.fields['doc_folio'].required = False
                self.fields['doc_type'].required = False
