from django import forms

class EmailForm(forms.Form):
    email_address = forms.EmailField()
    subject = forms.CharField()
    message = forms.CharField(widget = forms.Textarea)
    