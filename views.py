from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import View
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from django.core.exceptions import ValidationError

from .forms import PevForm, PevForm2, PevForm3
from .models import Pev, PevTipoResiduo

from cities_light import models as model_cities
from cities_light.models import Region, City


#se alterar, alterar também PevSearch
@login_required(login_url='/accounts/login')
def listar(request):
	pev_list = Pev.objects.all().only('nome','tipo', 'cidade')
	paginator = Paginator(pev_list, 5)

	page = request.GET.get('page')

	lista_uf = Region.objects.filter(country__id = 31).order_by('name')
	try: 

		pevs = paginator.page(page)
	except PageNotAnInteger:
		pevs = paginator.page(1)
	except EmptyPage:
		pevs = paginator.page(paginator.num_pages)

	return render(request, 'pev/listar.html', {
		'pevs': pevs,
		'lista_uf': lista_uf
	})



@login_required(login_url='/accounts/login')
def render_to_response(self, region):
	queryset = City.objects.filter(region__id = region)
	data = serializers.serialize('json', queryset)
	return HttpResponse(data, content_type='application/json')



@login_required(login_url='/accounts/login')
def listar_vinculo(request, pev_id):
	list = PevTipoResiduo.objects.filter(pev__id = pev_id)
	pev = Pev.objects.get(pk = pev_id)

	paginator = Paginator(list, 10)

	page = request.GET.get('page')

	try:
		pevs = paginator.page(page)
	except PageNotAnInteger:
		pevs = paginator.page(1)
	except EmptyPage:
		pevs = paginator.page(paginator.num_pages)

	return render(request, 'pev/pev_form3.html', 
		{ 'pevs': pevs,
		  'pev': pev
		})



class CepSearch(View):
	form_class = PevForm
	template_name = 'pev/pev_form.html'

	def post(self, request, *args, **kwargs):
		cep = self.request.POST.get('temp')
		if(cep != None and cep != ''):
			cep = cep.replace('.','')
			cep = cep.replace('-','')
			temp = Pev()
			temp.cep = cep
			result = _search_correio(temp)
			if(result != None):
				pev = result
				form = PevForm(initial={'cep': cep, 'bairro': pev.bairro, 'logradouro': pev.logradouro, 'latitude': pev.latitude, 'longitude': pev.longitude})
				form.fields['cidade'].queryset = City.objects.filter(region__id = pev.cidade.region.id)
				form.fields['cidade'].initial = pev.cidade.id

				return render(request, 'pev/pev_form1.html', {'form': form })
			else:
				form = PevForm()
				messages.add_message(request, messages.WARNING, 'CEP não encontrado.')			
				return render(request, self.template_name, {'form': form })
		else:
			form = PevForm()
			messages.add_message(request, messages.WARNING, 'Campo CEP deve ser preenchido.')
			return render(request, self.template_name, {'form': form })



class CepSearchUpdate(View):
	form_class = PevForm

	def post(self, request, *args, **kwargs):
		cep = self.request.POST.get('temp')
		pev_id = kwargs['pev_id']

		if(cep != None and cep != ''):
			cep = cep.replace('.','')
			cep = cep.replace('-','')
			temp = Pev()
			temp.cep = cep
			result = _search_correio(temp)
			if(result != None):
				pev = result
				result = Pev.objects.get(pk = pev_id)
				form = PevForm(initial={'nome': result.nome, 'tipo': result.tipo, 'cep': cep, 'bairro': pev.bairro, 'logradouro': pev.logradouro, 'latitude': pev.latitude, 'longitude': pev.longitude})
				form.fields['cidade'].queryset = City.objects.filter(region__id = pev.cidade.region.id)
				form.fields['cidade'].initial = pev.cidade.id

				return render(request, 'pev/pev_form_editar1.html', {'form': form, 'pev_id': pev_id })
			else:
				form = PevForm()
				messages.add_message(request, messages.WARNING, 'CEP não encontrado.')			
				return render(request, self.template_name, {'form': form })
		else:
			form = PevForm()
			messages.add_message(request, messages.WARNING, 'Campo CEP deve ser preenchido.')
			return render(request, self.template_name, {'form': form })





class PevSearch(View):
	form_class = PevForm
	template_name = 'pev/listar.html'

	def post(self, request, *args, **kwargs):
		nome = self.request.POST.get('nome_search')
		tipo = self.request.POST.get('tipo_search')
		uf = self.request.POST.get('uf')

		form = PevForm()
	
		if(nome == '' and tipo == '' and uf == ''):
			messages.add_message(request, messages.WARNING, 'Ao menos um campo deve ser selecionado.')
			
			## igual listar
			pev_list = Pev.objects.all().only('nome','tipo')  #adicionar cidade e uf
			
		else:
			pev_list = None
			if(nome != ''):
				pev_list = Pev.objects.filter(nome__icontains = str(nome))
			if(tipo != ''):
				if(pev_list == None):
					pev_list = Pev.objects.filter(tipo = tipo)
				else:
					pev_list = pev_list.filter(tipo = tipo)
			if(uf != ''):
				if(pev_list == None):
					pev_list = Pev.objects.filter(cidade__region__id = uf)
				else:
					pev_list = pev_list.filter(cidade__region__id = uf)
		
		paginator = Paginator(pev_list, 5)
		page = request.GET.get('page')
		lista_uf = Region.objects.filter(country__id = 31).order_by('name')
		try: 
			pevs = paginator.page(page)
		except PageNotAnInteger:
			pevs = paginator.page(1)
		except EmptyPage:
			pevs = paginator.page(paginator.num_pages)

		return render(request, 'pev/listar.html', {
			'pevs': pevs,
			'lista_uf': lista_uf
		})



class PevInsert(CreateView):
	template_name = 'pev/pev_form.html'
	model = Pev
	form_class = PevForm

	def form_invalid(self, form):
		if(form.instance.nome == ''):
			messages.add_message(self.request, messages.WARNING, 'O campo Nome deve ser preenchido.')
		if(form.instance.tipo == ''):
			messages.add_message(self.request, messages.WARNING, 'O campo Tipo deve ser preenchido.')
		if(form.instance.logradouro == ''):
			messages.add_message(self.request, messages.WARNING, 'O campo Logradouro deve ser preenchido.')
		if(form.instance.bairro == ''):
			messages.add_message(self.request, messages.WARNING, 'O campo Bairro deve ser preenchido.')
		if(form.instance.cep == ''):
			messages.add_message(self.request, messages.WARNING, 'O campo CEP deve ser preenchido.')
		if(self.request.POST.get('cidade') == ''):
			messages.add_message(self.request, messages.WARNING, 'O campo Cidade deve ser preenchido.')

		return render(self.request, 'pev/pev_form1.html', {'form': form })

	def form_valid(self, form):
		super(PevInsert, self).form_valid(form)
		return HttpResponseRedirect(self.get_success_url())

	def get_success_url(self):
		return reverse('pev:listar_vinculo', kwargs={'pev_id': self.object.id})



class PevInsertSemCep(CreateView):
	template_name = 'pev/pev_form2.html'
	model = Pev
	form_class = PevForm2

	def get_context_data(self, **kwargs):
		context = super(PevInsertSemCep, self).get_context_data(**kwargs)
		lista_uf = Region.objects.filter(country__id = 31).order_by('name')
		context['lista_uf'] = lista_uf
		return context

	def form_invalid(self, form):
		if(form.instance.nome == ''):
			messages.add_message(self.request, messages.WARNING, 'O campo Nome deve ser preenchido.')
		if(form.instance.tipo == ''):
			messages.add_message(self.request, messages.WARNING, 'O campo Tipo deve ser preenchido.')
		if(form.instance.logradouro == ''):
			messages.add_message(self.request, messages.WARNING, 'O campo Logradouro deve ser preenchido.')
		if(form.instance.bairro == ''):
			messages.add_message(self.request, messages.WARNING, 'O campo Bairro deve ser preenchido.')
		if(self.request.POST.get('cidade') == ''):
			messages.add_message(self.request, messages.WARNING, 'O campo Cidade deve ser preenchido.')
		return render(self.request, self.template_name, {'form': form })

	def form_valid(self, form):
		pev = Pev()
		pev.logradouro = form.instance.logradouro
		pev.bairro = form.instance.bairro
		form.instance.cidade = City.objects.get(pk=int(self.request.POST.get('cidade')))
		pev.cidade = form.instance.cidade
		pev = _search_lat_lng(pev, 0)
		form.instance.latitude = pev.latitude
		form.instance.longitude = pev.longitude
		super(PevInsertSemCep, self).form_valid(form)
		return HttpResponseRedirect(self.get_success_url())

	def get_success_url(self):
		return reverse('pev:listar_vinculo', kwargs={'pev_id': self.object.pk})



class PevVincular(View):
	def post(self, request, *args, **kwargs):
		if 'bt1' in request.POST:
			pev_id = self.request.POST.get('pev_id')
			tipo_residuo = self.request.POST.get('tipo_residuo')

			if(tipo_residuo == ''):
				messages.add_message(request, messages.WARNING, 'Tipo de Resíduo deve ser selecionado.')			
			else:
				result = PevTipoResiduo.objects.filter(pev__id = pev_id, tipo = tipo_residuo)
				if(len(result) == 0):
					objeto = PevTipoResiduo()
					objeto.pev = Pev.objects.get(pk=pev_id)
					objeto.tipo = tipo_residuo
					objeto.save()
				else:
					messages.add_message(request, messages.WARNING, 'Tipo de resíduo já vinculado.')

			##igual listar_vinculo
			list = PevTipoResiduo.objects.filter(pev__id = pev_id)
			pev = Pev.objects.get(pk = pev_id)

			paginator = Paginator(list, 10)

			page = request.GET.get('page')

			try:
				pevs = paginator.page(page)
			except PageNotAnInteger:
				pevs = paginator.page(1)
			except EmptyPage:
				pevs = paginator.page(paginator.num_pages)

			return render(request, 'pev/pev_form3.html', 
				{ 'pevs': pevs,
				  'pev': pev
				})
		else:
			if 'bt2' in request.POST:
				pev_id = self.request.POST.get('pev_id')
				list = PevTipoResiduo.objects.filter(pev__id = pev_id)
				if(len(list) > 0):
					return HttpResponseRedirect(reverse('pev:listar'))
				else:
					messages.add_message(request, messages.WARNING, 'Ao menos um Tipo de Resíduo deve ser vinculado.')

					##igual listar_vinculo
					list = PevTipoResiduo.objects.filter(pev__id = pev_id)
					pev = Pev.objects.get(pk = pev_id)

					paginator = Paginator(list, 10)

					page = request.GET.get('page')

					try:
						pevs = paginator.page(page)
					except PageNotAnInteger:
						pevs = paginator.page(1)
					except EmptyPage:
						pevs = paginator.page(paginator.num_pages)

					return render(request, 'pev/pev_form3.html', 
						{ 'pevs': pevs,
						  'pev': pev
						})
				
			

class PevUpdate(UpdateView):
	template_name = 'pev/pev_form_editar.html'
	model = Pev
	form_class = PevForm

	def get_context_data(self, **kwargs):
		context = super(PevUpdate, self).get_context_data(**kwargs)
		context['cep'] = self.object.cep
		context['pev_id'] = self.object.pk
		return context

	def form_invalid(self, form):
		cep = form.instance.cep
		if(cep != None and cep != ''):
			cep = cep.replace('.','')
			cep = cep.replace('-','')
			temp = Pev()
			temp.cep = cep
			result = _search_correio(temp)
			if(result != None):
				pev = result
				form2 = PevForm(initial={'cep': cep, 'bairro': pev.bairro, 'logradouro': pev.logradouro, 'latitude': pev.latitude, 'longitude': pev.longitude})
				form2.fields['cidade'].queryset = City.objects.filter(region__id = pev.cidade.region.id)
				form2.fields['cidade'].initial = pev.cidade.id
				if(form.instance.nome == ''):
					messages.add_message(self.request, messages.WARNING, 'O campo Nome deve ser preenchido.')
				if(form.instance.tipo == ''):
					messages.add_message(self.request, messages.WARNING, 'O campo Tipo deve ser preenchido.')
				form = form2
		else:
			if(form.instance.nome == ''):
				messages.add_message(self.request, messages.WARNING, 'O campo Nome deve ser preenchido.')
			if(form.instance.tipo == ''):
				messages.add_message(self.request, messages.WARNING, 'O campo Tipo deve ser preenchido.')
			if(form.instance.logradouro == ''):
				messages.add_message(self.request, messages.WARNING, 'O campo Logradouro deve ser preenchido.')
			if(form.instance.bairro == ''):
				messages.add_message(self.request, messages.WARNING, 'O campo Bairro deve ser preenchido.')
			if(self.request.POST.get('cidade') == ''):
				messages.add_message(self.request, messages.WARNING, 'O campo Cidade deve ser preenchido.')

		return render(self.request, 'pev/pev_form_editar1.html', {'form': form })

	def form_valid(self, form):
		super(PevUpdate, self).form_valid(form)
		return HttpResponseRedirect(self.get_success_url())

	def get_success_url(self):
		return reverse('pev:listar_vinculo', kwargs={'pev_id': self.object.id})



class PevUpdate1(UpdateView):
	template_name = 'pev/pev_form_editar1.html'
	model = Pev
	form_class = PevForm

	def get_context_data(self, **kwargs):
		context = super(PevUpdate1, self).get_context_data(**kwargs)
		context['pev_id'] = self.object.pk
		return context

	def form_invalid(self, form):
		if(form.instance.nome == ''):
			messages.add_message(self.request, messages.WARNING, 'O campo Nome deve ser preenchido.')
		if(form.instance.tipo == ''):
			messages.add_message(self.request, messages.WARNING, 'O campo Tipo deve ser preenchido.')
		if(form.instance.logradouro == ''):
			messages.add_message(self.request, messages.WARNING, 'O campo Logradouro deve ser preenchido.')
		if(form.instance.bairro == ''):
			messages.add_message(self.request, messages.WARNING, 'O campo Bairro deve ser preenchido.')
		if(form.instance.cep == ''):
			messages.add_message(self.request, messages.WARNING, 'O campo CEP deve ser preenchido.')
		if(self.request.POST.get('cidade') == ''):
			messages.add_message(self.request, messages.WARNING, 'O campo Cidade deve ser preenchido.')

		return render(self.request, 'pev/pev_form1.html', {'form': form })

	def form_valid(self, form):
		super(PevInsert, self).form_valid(form)
		return HttpResponseRedirect(self.get_success_url())

	def get_success_url(self):
		return reverse('pev:listar_vinculo', kwargs={'pev_id': self.object.id})



class PevUpdate2(UpdateView):
	template_name = 'pev/pev_form_editar2.html'
	model = Pev
	form_class = PevForm3

	def get_context_data(self, **kwargs):
		context = super(PevUpdate2, self).get_context_data(**kwargs)
		context['pev_id'] = self.object.pk

		lista_uf = Region.objects.filter(country__id = 31).order_by('name')
		context['lista_uf'] = lista_uf

		context['region_id'] = self.object.cidade.region.pk
		lista_cidade = City.objects.filter(region__id = self.object.cidade.region.pk)
		context['lista_cidade'] = lista_cidade
		context['cidade_id'] = self.object.cidade.pk

		return context

	def form_invalid(self, form):
		if(form.instance.nome == ''):
			messages.add_message(self.request, messages.WARNING, 'O campo Nome deve ser preenchido.')
		if(form.instance.tipo == ''):
			messages.add_message(self.request, messages.WARNING, 'O campo Tipo deve ser preenchido.')
		if(form.instance.logradouro == ''):
			messages.add_message(self.request, messages.WARNING, 'O campo Logradouro deve ser preenchido.')
		if(form.instance.bairro == ''):
			messages.add_message(self.request, messages.WARNING, 'O campo Bairro deve ser preenchido.')
		if(self.request.POST.get('cidade') == ''):
			messages.add_message(self.request, messages.WARNING, 'O campo Cidade deve ser preenchido.')

		lista_uf = Region.objects.filter(country__id = 31).order_by('name')
		lista_cidade = City.objects.filter(region__id = self.object.cidade.region.pk)

		return render(self.request, self.template_name, {'form': form, 'pev_id': self.object.pk, 'lista_uf': lista_uf, 'region_id': self.object.cidade.region.pk, 'lista_cidade': lista_cidade, 'cidade_id': self.object.cidade.pk })

	def form_valid(self, form):
		pev = Pev()
		pev.logradouro = form.instance.logradouro
		pev.bairro = form.instance.bairro
		
		cidade = self.request.POST.get('cidade')
		if(cidade == '' or cidade == None):
			messages.add_message(self.request, messages.WARNING, 'O campo Cidade deve ser preenchido.')

			lista_uf = Region.objects.filter(country__id = 31).order_by('name')
			lista_cidade = City.objects.filter(region__id = self.object.cidade.region.pk)

			return render(self.request, self.template_name, {'form': form, 'pev_id': self.object.pk, 'lista_uf': lista_uf, 'region_id': self.object.cidade.region.pk, 'lista_cidade': lista_cidade, 'cidade_id': self.object.cidade.pk })

		else:
			form.instance.cidade = City.objects.get(pk=int(self.object.cidade.pk))
			pev.cidade = form.instance.cidade
			pev = _search_lat_lng(pev, 0)
			form.instance.latitude = pev.latitude
			form.instance.longitude = pev.longitude
			super(PevUpdate2, self).form_valid(form)
			return HttpResponseRedirect(self.get_success_url())

	def get_success_url(self):
		return reverse('pev:listar_vinculo', kwargs={'pev_id': self.object.pk})



class PevDelete(DeleteView):	
	model = Pev
	
	def get_success_url(self):
		messages.add_message(self.request, messages.SUCCESS, 'Exclusão efetuada com sucesso.')
		return reverse('pev:listar')


				



######Private methods
def _get_cidade(cidade_nome, uf_abreviacao):

	dict_uf = {'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas', 
		'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo', 
		'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
		'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná', 'PE': 'Pernambuco',
		'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte', 'RS': 'Rio Grande do Sul',
		'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina', 'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'}

	search = model_cities.to_search(cidade_nome)
	nome_uf = None
	for key, value in dict_uf.items():
		if key in uf_abreviacao:
			nome_uf = value	
	region = Region.objects.filter(country__id = 31, name = nome_uf)
	if len(region) == 0:
		region = Region.objects.filter(country__id = 31, alternate_names__contains = nome_uf)
	
	if len(region) > 0:
		cidade = City.objects.filter(slug = search, region__id = region[0].id)
		if len(cidade) == 1:
			return cidade[0]
		else:
			return None
	else:
		return None


def _search_lat_lng(temp, numero):
	
	from socket import timeout
	import urllib.request
	import json
	
	search_url = None
	raw = None

	if(temp.cep == None):
		search_url = "http://maps.googleapis.com/maps/api/geocode/json?address=99999999"
	else:
		if numero == 0 and temp.cep != '' and temp.cep != None:
			search_url = "http://maps.googleapis.com/maps/api/geocode/json?address=" + temp.cep
		elif numero == 0 and temp.cep == '' or temp.cep == None:
			address_text = temp.logradouro + ',' + temp.bairro + ',' + temp.cidade.name + ',' + temp.cidade.region.name +  ', Brazil'
			address_text = urllib.parse.quote(address_text)
			search_url = "http://maps.googleapis.com/maps/api/geocode/json?address=" + address_text
		elif numero == 1:
			address_text = temp.logradouro + ',' + temp.bairro + ',' + temp.cidade.name + ',' + temp.cidade.region.name +  ', Brazil'
			address_text = urllib.parse.quote(address_text)
			search_url = "http://maps.googleapis.com/maps/api/geocode/json?address=" + address_text
		elif numero == 2:
			address_text = temp.bairro + ',' + temp.cidade.name + ',' + temp.cidade.region.name +  ', Brazil'
			address_text = urllib.parse.quote(address_text)
			search_url = "http://maps.googleapis.com/maps/api/geocode/json?address=" + address_text
		elif numero == 3:
			address_text = temp.cidade.name + ',' + temp.cidade.region.name +  ', Brazil'
			address_text = urllib.parse.quote(address_text)
			search_url = "http://maps.googleapis.com/maps/api/geocode/json?address=" + address_text
	
	print(search_url)

	try:
    		raw = urllib.request.urlopen(search_url, timeout=10)
	except (urllib.error.HTTPError, urllib.error.URLError) as error:
    		print(error)
	except timeout:
    		print('socket timed out - URL ' + search_url)
	
	if(raw):
		js = raw.read()
		js = js.decode("utf-8")
		wjdata = json.loads(js)

		if(wjdata['status'] == 'OK'):
			temp.latitude = wjdata['results'][0]['geometry']['location']['lat']
			temp.longitude = wjdata['results'][0]['geometry']['location']['lng']
		else:
			_search_lat_lng(temp, numero + 1)
	return temp



def _search_correio(temp):
	if(temp.cep.isnumeric()):
		search_url = "http://republicavirtual.com.br/web_cep.php?cep=" + temp.cep
		import simplejson as json
		import urllib.request
		import re
	
		raw = urllib.request.urlopen(search_url)
		js = raw.readlines()

		#temp = Pev()
		temp.nome = re.sub('<[^>]*>', '', js[2].decode("latin1"))
		if('1' in temp.nome):
			uf_abreviacao = re.sub('<[^>]*>', '', js[4].decode("latin1"))
			cidade_nome = re.sub('<[^>]*>', '', js[5].decode("latin1"))
			result = _get_cidade(cidade_nome, uf_abreviacao)		
			if(result):
				temp.cidade = result
				if js[6] != None:
					temp.bairro = re.sub('<[^>]*>', '', js[6].decode("latin1"))
				if js[7] != None or js[8] != None:
					temp.logradouro = re.sub('<[^>]*>', '', js[7].decode("latin1") + ' ' + js[8].decode("latin1"))

				temp = _search_lat_lng(temp, 0)
				return temp
			else:
				return None
		else:
			return None 
	else:
		return None
