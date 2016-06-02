
from __future__ import unicode_literals

from django.db import models
from cities_light.models import City, Region


TIPO_PEV = (
	('PE', 'Ponto de entrega voluntária'),
	('ER', 'Empresa que recebe'),
	('EB', 'Empresa que busca'),
	('OR', 'Órgão governamental que recebe'),
	('OB', 'Órgão governamental que busca'),
	('CB', 'Cooperativa de catadores que busca'),
	('CR', 'Cooperativa de catadores que recebe'),
	('ST', 'Site de troca de objetos usados'), 
)
#qualquer alteração alterar tb
# pev/listar.html
# pev/forms.py

TIPO_RESIDUO = (
	('CO', 'Computador usado'),
	('ME', 'Metal'),
	('MO', 'Móveis usados'),
	('PA', 'Papel'),
	('PL', 'Plástico'),
	('VI', 'Vidro'),
)

class Pev(models.Model):
	nome = models.CharField(max_length = 256, blank=False)
	tipo = models.CharField(max_length = 2, choices=TIPO_PEV, blank=False)
	logradouro = models.CharField(max_length=256, blank=False)
	complemento = models.CharField(max_length=256, blank=True)
	numero = models.CharField(max_length=20, blank=True)
	bairro = models.CharField(max_length=256, blank=False)
	cep = models.CharField(max_length=15, blank=True)
	cidade = models.ForeignKey(City, null=False)

	#http://stackoverflow.com/questions/15965166/what-is-the-maximum-length-of-latitude-and-longitude
	latitude = models.CharField(max_length=17, blank=False)
	longitude = models.CharField(max_length=17, blank=False)

	def __unicode__(self):
		return self.nome

	def __str__(self):
		return self.nome

	def tipo_name(self):
		for choice in TIPO_PEV:
			if (choice[0] == self.tipo):
				return choice[1]
		return '?'

	class Meta:
		ordering = ["nome"]



class PevTipoResiduo(models.Model):
	pev = models.ForeignKey(Pev, null=False)
	tipo = models.CharField(max_length = 2, choices=TIPO_RESIDUO, blank=False)

	def tipo_name(self):
		for choice in TIPO_RESIDUO:
			if (choice[0] == self.tipo):
				return choice[1]
		return '?'
