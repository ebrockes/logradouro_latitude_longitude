from django.conf.urls import url

from .views import PevInsert, PevInsertSemCep
from .views import CepSearch, CepSearchUpdate, PevSearch
from .views import PevUpdate, PevUpdate1, PevUpdate2
from .views import PevVincular
from .views import PevDelete
from .views import listar, render_to_response, listar_vinculo

from django.contrib.auth.decorators import login_required

urlpatterns = [
	url(r'^$', listar, name='listar'),
	url(r'^(?P<region>\d+)/a/$', render_to_response, name='render_to_response'),
	url(r'^(?P<pev_id>\d+)/v/$', listar_vinculo, name='listar_vinculo'),

	url(r'^search/cep/$', login_required(CepSearch.as_view()), name='cepsearch'),
	url(r'^search/cep/(?P<pev_id>\d+)/$', login_required(CepSearchUpdate.as_view()), name='cepsearchupdate'),

	url(r'^search/pev/$', login_required(PevSearch.as_view()), name='pevsearch'),

	url(r'^novo/$', login_required(PevInsert.as_view()), name='novo'),
	url(r'^novo2/$', login_required(PevInsertSemCep.as_view()), name='novo2'),

	url(r'^(?P<pev_id>\d+)/vincular/$', login_required(PevVincular.as_view()), name='vincular'),

	url(r'^(?P<pk>\d+)/editar/$', login_required(PevUpdate.as_view()), name='editar'),
	url(r'^(?P<pk>\d+)/editar2/$', login_required(PevUpdate1.as_view()), name='editar2'),
	url(r'^(?P<pk>\d+)/editar3/$', login_required(PevUpdate2.as_view()), name='editar3'),

	url(r'^(?P<pk>\d+)/delete/$', login_required(PevDelete.as_view()), name='delete'),
]
