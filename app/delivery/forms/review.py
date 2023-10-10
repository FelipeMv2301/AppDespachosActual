from django import forms


class ReviewForm(forms.Form):
    orders = forms.CharField(
        label='Pedido(s)',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'mb-2 textfield search-bar',
                'aria-controls': 'myResults',
                'placeholder': '2307483',
            }
        )
    )
