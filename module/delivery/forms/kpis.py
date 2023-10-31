from datetime import date, timedelta

from django import forms


class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        label='Desde',
        required=True,
        disabled=False,
        initial=(date.today() + timedelta(days=-30)).strftime('%Y-%m-%d'),
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'mb-2 textfield'
            }
        )
    )
    end_date = forms.DateField(
        label='Hasta',
        required=True,
        disabled=False,
        initial=date.today().strftime('%Y-%m-%d'),
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'mb-2 textfield'
            }
        )
    )
