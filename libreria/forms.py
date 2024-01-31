from django import forms


class MiFormulario(forms.Form):

    texto = forms.CharField(widget=forms.Textarea, required=False)

