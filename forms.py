from django import forms
from .models import Pev
from cities_light.models import City

TIPO_PEV = (
	('', 'Selecione...'),
	('PE', 'Ponto de entrega voluntária'),
	('ER', 'Empresa que recebe'),
	('EB', 'Empresa que busca'),
	('OR', 'Órgão governamental que recebe'),
	('OB', 'Órgão governamental que busca'),
	('CB', 'Cooperativa de catadores que busca'),
	('CR', 'Cooperativa de catadores que recebe'),
	('ST', 'Site de troca de objetos usados'), 
)

class PevForm(forms.ModelForm):
	nome = forms.CharField(max_length=256, widget=forms.TextInput(attrs={'size':'50'}), required=True)
	tipo = forms.ChoiceField(widget = forms.Select(), choices=TIPO_PEV, required=True)
	logradouro = forms.CharField(max_length=256, widget=forms.TextInput(attrs={'size':'50'}), required=True)
	complemento = forms.CharField(max_length=256, widget=forms.TextInput(attrs={'size':'50'}), required=False)
	numero = forms.CharField(max_length=256, widget=forms.TextInput(attrs={'size':'15'}), required=False)
	bairro = forms.CharField(max_length=256, widget=forms.TextInput(attrs={'size':'50'}), required=True)
	cep = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'type': 'number', 'size':'15'}), required=False)
	cidade = forms.ModelChoiceField(queryset=City.objects.filter(region__country__id = 31), required=True) 
	latitude = forms.CharField(max_length=17, widget=forms.TextInput(attrs={'size':'15'}), required=False)
	longitude = forms.CharField(max_length=17, widget=forms.TextInput(attrs={'size':'15'}), required=False)		

	class Meta:
		model = Pev
		fields = ('nome','tipo','logradouro','complemento','numero','bairro','cep','cidade','latitude','longitude',)



class PevForm2(forms.ModelForm):
	nome = forms.CharField(max_length=256, widget=forms.TextInput(attrs={'size':'50'}), required=True)
	tipo = forms.ChoiceField(widget = forms.Select(), choices=TIPO_PEV, required=True)
	logradouro = forms.CharField(max_length=256, widget=forms.TextInput(attrs={'size':'50'}), required=True)
	complemento = forms.CharField(max_length=256, widget=forms.TextInput(attrs={'size':'50'}), required=False)
	numero = forms.CharField(max_length=256, widget=forms.TextInput(attrs={'size':'15'}), required=False)
	bairro = forms.CharField(max_length=256, widget=forms.TextInput(attrs={'size':'50'}), required=True)

	class Meta:
		model = Pev
		exclude = ('latitude', 'longitude', 'cidade', )



class PevForm3(forms.ModelForm):
	nome = forms.CharField(max_length=256, widget=forms.TextInput(attrs={'size':'50'}), required=True)
	tipo = forms.ChoiceField(widget = forms.Select(), choices=TIPO_PEV, required=True)
	logradouro = forms.CharField(max_length=256, widget=forms.TextInput(attrs={'size':'50'}), required=True)
	complemento = forms.CharField(max_length=256, widget=forms.TextInput(attrs={'size':'50'}), required=False)
	numero = forms.CharField(max_length=256, widget=forms.TextInput(attrs={'size':'15'}), required=False)
	bairro = forms.CharField(max_length=256, widget=forms.TextInput(attrs={'size':'50'}), required=True)
	latitude = forms.CharField(max_length=17, widget=forms.TextInput(attrs={'size':'15'}), required=False)
	longitude = forms.CharField(max_length=17, widget=forms.TextInput(attrs={'size':'15'}), required=False)		

	class Meta:
		model = Pev
		exclude = ('cidade',)



