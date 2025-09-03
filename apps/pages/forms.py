from django import forms

from apps.pages.models import ContactModel


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactModel
        exclude = ['is_read', 'comment']


    def clean(self):
        print("1. object level validation")
        print(self.cleaned_data)
        return super().clean()

    def clean_phone_number(self):
        print("2. field level validation")
        phone_number: str = self.cleaned_data.get('phone_number')
        if not phone_number.startswith('+'):
            raise forms.ValidationError("Phone number should start with +")
        return self.cleaned_data.get('phone_number')
