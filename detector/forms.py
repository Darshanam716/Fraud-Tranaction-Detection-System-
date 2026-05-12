from django import forms


class TransactionForm(forms.Form):
    time = forms.FloatField(
        label='Time (seconds elapsed)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': '0.0'}),
        initial=0.0
    )
    amount = forms.FloatField(
        label='Transaction Amount ($)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': '100.00', 'min': '0'}),
        initial=100.0
    )

    # Generate V1–V28 fields dynamically
    for i in range(1, 29):
        locals()[f'v{i}'] = forms.FloatField(
            label=f'V{i}',
            widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': '0.0'}),
            initial=0.0
        )

    def get_feature_vector(self):
        """Return features in order: Time, V1..V28, Amount"""
        data = self.cleaned_data
        features = [data['time']]
        for i in range(1, 29):
            features.append(data[f'v{i}'])
        features.append(data['amount'])
        return features


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='Upload CSV File',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv'}),
        help_text='CSV must have columns: Time, V1–V28, Amount (no Class column needed)'
    )
