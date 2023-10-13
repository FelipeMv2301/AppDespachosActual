from django import forms
from django.utils.functional import SimpleLazyObject

from app.delivery.models.branch import Branch
from app.delivery.models.pay_type import PayType
from app.delivery.models.service import Service as DelivServ
from app.delivery.models.type import Type
from app.general.models.muni import Muni
from app.general.models.service import Service
from app.order.forms.validators.delivery_form import DeliveryFormValidator


class DeliveryForm(forms.Form):
    orders = forms.CharField(
        label='Pedido(s)',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'mb-2 textfield search-bar',
                'aria-controls': 'myResults',
                'placeholder': '2303467',
                'autocomplete': 'off',
            }
        ),
        validators=[DeliveryFormValidator().validate_order],
    )
    obs = forms.CharField(
        label='Observaciones de entrega',
        max_length='255',
        required=False,
        disabled=False,
        widget=forms.TextInput(
            attrs={
                'class': 'mb-2 textfield',
                'maxlength': '255',
                'oninput': 'this.value = this.value.slice(0, 255)',
            }
        )
    )

    def __init__(self,
                 user: SimpleLazyObject,
                 can_edit_form: bool,
                 can_edit_commit_date: bool,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if can_edit_commit_date or can_edit_form:
            self.fields['commit_date'] = forms.DateField(
                label='Fecha de compromiso',
                required=True,
                disabled=False,
                widget=forms.DateInput(
                    attrs={
                        'class': 'mb-2 textfield',
                        'type': 'date',
                    }
                ),
                validators=[DeliveryFormValidator().validate_date],
            )
        if can_edit_form:
            if can_edit_commit_date:
                self.fields['commit_date'].required = False

            self.fields['contact_first_name'] = forms.CharField(
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
                validators=[DeliveryFormValidator().validate_contact_names],
            )
            self.fields['contact_last_name'] = forms.CharField(
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
                validators=[DeliveryFormValidator().validate_contact_names],
            )
            self.fields['contact_email_addr'] = forms.EmailField(
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
                )
            )
            self.fields['contact_phone1'] = forms.CharField(
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
                validators=[DeliveryFormValidator().validate_phone_num],
            )
            self.fields['contact_phone2'] = forms.CharField(
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
                validators=[DeliveryFormValidator().validate_phone_num],
            )
            self.fields['contact_mobile_phone'] = forms.CharField(
                label='Celular de contacto',
                max_length=100,
                required=False,
                disabled=False,
                widget=forms.TextInput(
                    attrs={
                        'class': 'mb-2 textfield',
                        'oninput': ('this.value = this.value.replace(/[^0-9+]+/g, "");',
                                    'this.value = this.value.slice(0, 100);'),
                        'placeholder': '+56953093750',
                        'maxlength': '100',
                    }
                ),
                validators=[DeliveryFormValidator().validate_phone_num],
            )
            self.fields['deliv_st_and_num'] = forms.CharField(
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
                validators=[DeliveryFormValidator().validate_addr],
            )
            self.fields['deliv_addr_complement'] = forms.CharField(
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
                validators=[DeliveryFormValidator().validate_addr],
            )
            self.fields['deliv_muni'] = forms.ChoiceField(
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
                validators=[DeliveryFormValidator().validate_muni],
            )
            self.fields['carrier'] = forms.ChoiceField(
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
                        'onchange': 'searchDeliveryOption()',
                    }
                ),
                validators=[DeliveryFormValidator().validate_carrier],
            )
            self.fields['deliv_type'] = forms.ChoiceField(
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
                validators=[DeliveryFormValidator().validate_deliv_type],
            )
            self.fields['deliv_service'] = forms.ChoiceField(
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
                validators=[DeliveryFormValidator().validate_deliv_serv],
            )
            self.fields['deliv_pay_type'] = forms.ChoiceField(
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
                validators=[DeliveryFormValidator().validate_deliv_pay_type],
            )
            self.fields['branch'] = forms.ChoiceField(
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
                validators=[DeliveryFormValidator().validate_branch],
            )
