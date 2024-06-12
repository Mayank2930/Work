from django import forms
from .models import Merchant


class MerchantForm(forms.ModelForm):
    class Meta:
        model = Merchant
        fields = ('file_name',
                  'tid',
                  'aggregator_module',
                  'legal_name',
                  'primary_email',
                  'secondary_email',
                  'bcc_email',
                  )
