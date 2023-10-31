from datetime import date, timedelta

from django import forms

from module.delivery.models.status import Status
from app.general.models.service import Service


class PanelForm(forms.Form):
    status = forms.ChoiceField(
        label='Estado de entrega',
        required=False,
        disabled=False,
        choices=[(s.code, s.name)
                 for s in (Status.objects.filter(enabled=True)
                           .order_by('name'))],
        widget=forms.Select(
            attrs={
                'class': 'mb-2 textfield',
            }
        ),
    )
    carrier = forms.ChoiceField(
        label='Vía de entrega',
        required=False,
        disabled=False,
        choices=[(s.code, s.name)
                 for s in (Service.objects.filter(enabled=True,
                                                  is_carrier=True)
                           .order_by('name'))],
        widget=forms.Select(
            attrs={
                'class': 'mb-2 textfield',
            }
        ),
    )
    updtd_commit_start_date = forms.DateField(
        label='Desde',
        required=False,
        disabled=False,
        initial=(date.today() + timedelta(days=-30)).strftime('%Y-%m-%d'),
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'mb-2 textfield'
            }
        )
    )
    updtd_commit_end_date = forms.DateField(
        label='Hasta',
        required=False,
        disabled=False,
        initial=date.today().strftime('%Y-%m-%d'),
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'mb-2 textfield'
            }
        )
    )
    issue_start_date = forms.DateField(
        label='Desde',
        required=False,
        disabled=False,
        initial=(date.today() + timedelta(days=-30)).strftime('%Y-%m-%d'),
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'mb-2 textfield'
            }
        )
    )
    issue_end_date = forms.DateField(
        label='Hasta',
        required=False,
        disabled=False,
        initial=date.today().strftime('%Y-%m-%d'),
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'mb-2 textfield'
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        status_choices = self.fields['status'].choices
        status_choices.append(('', 'Elija una opción'))
        self.fields['status'].choices = status_choices

        carrier_choices = self.fields['carrier'].choices
        carrier_choices.append(('', 'Elija una opción'))
        self.fields['carrier'].choices = carrier_choices
