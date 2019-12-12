from node import models
from django.forms import ModelForm
from . import cdmsportalfunc as cpf
from django.core.exceptions import ValidationError
from django import forms


class MoleculeForm(ModelForm):
    class Meta:
        model = models.Molecules
        fields = '__all__'


class SpecieForm(ModelForm):
    datearchived = forms.DateField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
        )

    dateactivated = forms.DateField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
        )

    class Meta:
        model = models.Species
        fields = '__all__'


class FilterForm(ModelForm):
    class Meta:
        model = models.QuantumNumbersFilter
        fields = '__all__'


class XsamsConversionForm(forms.Form):

    inurl = forms.URLField(
            label='Input URL',
            required=False,
            widget=forms.TextInput(
                attrs={'size': 50,
                       'title': 'Paste here a URL that delivers an XSAMS '
                                'document.',
                       }))
    infile = forms.FileField()
    format = forms.ChoiceField(
            choices=[("RAD 3D", "RAD 3D"), ("CSV", "CSV")], )

    def clean(self):
        infile = self.cleaned_data.get('infile')
        inurl = self.cleaned_data.get('inurl')
        if (infile and inurl):
            raise ValidationError('Give either input file or URL!')

        if inurl:
            try:
                data = cpf.urlopen(inurl)
            except Exception as err:
                raise ValidationError('Could not open given URL: %s' % err)
        elif infile:
            data = infile
        else:
            raise ValidationError('Give either input file or URL!')

        try:
            self.cleaned_data['result'] = cpf.applyStylesheet2File(data)
        except Exception as err:
            raise ValidationError('Could not transform XML file: %s' % err)

        return self.cleaned_data
