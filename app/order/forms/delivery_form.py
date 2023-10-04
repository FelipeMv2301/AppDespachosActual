from django import forms
from django.utils.functional import SimpleLazyObject

from app.delivery.models.branch import Branch
from app.delivery.models.pay_type import PayType
from app.delivery.models.service import Service as DelivServ
from app.delivery.models.type import Type
from app.general.models.muni import Muni
from app.general.models.service import Service


class DeliveryForm(forms.Form):
    orders = forms.CharField(
        label='Pedido(s)',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'mb-2 textfield search-bar',
                'aria-controls': 'myResults',
            }
        )
    )

    def __init__(self, user: SimpleLazyObject, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if self.user_can_edit_commit_date():
            self.fields['commit_date'] = forms.DateField(
                label='Fecha de compromiso',
                required=True,
                disabled=False,
                widget=forms.DateInput(
                    attrs={
                        'class': 'mb-2 textfield'
                    }
                )
            )
            self.fields['obs'] = forms.CharField(
                label='Observaciones de pedido',
                required=False,
                disabled=False,
                widget=forms.TextInput(
                    attrs={
                        'class': 'mb-2 textfield'
                    }
                )
            )
        else:
            self.fields['contact_first_name'] = forms.CharField(
                label='Nombre de contacto',
                required=True,
                disabled=False,
                widget=forms.TextInput(
                    attrs={
                        'class': 'mb-2 textfield'
                    }
                )
            )
            self.fields['contact_last_name'] = forms.CharField(
                label='Apellido de contacto',
                required=True,
                disabled=False,
                widget=forms.TextInput(
                    attrs={
                        'class': 'mb-2 textfield'
                    }
                )
            )
            self.fields['contact_email_addr'] = forms.EmailField(
                label='Correo electrónico de contacto',
                required=True,
                disabled=False,
                widget=forms.EmailInput(
                    attrs={
                        'class': 'mb-2 textfield'
                    }
                )
            )
            self.fields['contact_phone_number'] = forms.CharField(
                label='Teléfono de contacto',
                required=True,
                disabled=False,
                widget=forms.TextInput(
                    attrs={
                        'class': 'mb-2 textfield'
                    }
                )
            )
            self.fields['deliv_st_and_num'] = forms.CharField(
                label='Calle y numeración de entrega',
                required=True,
                disabled=False,
                widget=forms.TextInput(
                    attrs={
                        'class': 'mb-2 textfield'
                    }
                )
            )
            self.fields['deliv_addr_complement'] = forms.CharField(
                label='Complemento de dirección de entrega',
                required=True,
                disabled=False,
                widget=forms.TextInput(
                    attrs={
                        'class': 'mb-2 textfield'
                    }
                )
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
                )
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
                )
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
                )
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
                )
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
                )
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
                        'onchange': 'searchDeliveryOption()',
                    }
                )
            )
            self.fields['obs'] = forms.CharField(
                label='Observaciones de entrega',
                required=False,
                disabled=False,
                widget=forms.TextInput(
                    attrs={
                        'class': 'mb-2 textfield'
                    }
                )
            )

    def user_can_edit_commit_date(self):
        return self.user.has_perm(perm='order.edit_commit_date')
