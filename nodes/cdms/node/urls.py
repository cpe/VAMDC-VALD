# Optional:
# Use this file to connect views from views.py in the same
# directory to their URLs.
from django.contrib.auth.views import login, logout

#from django.conf.urls.defaults import *
from django.conf.urls import url, include
from django.conf import settings

from django.views.decorators.cache import cache_page
from . import views

#
urlpatterns = [
#                       settings.NODENAME+'.node.views',
                       url(r'^$', views.index, name = 'index'),
                       url(r'^cdms$', views.index, name ='cdms'),
                       url(r'^home', views.index, name = 'home'),
                       url(r'^queryPage', views.queryPage, name = 'queryPage'),                       
                       url(r'^queryForm', views.query_form, name = 'query_form'), 
                       url(r'^querySpecies', views.queryspecies, name = 'querySpecies'),
                       url(r'^html_list/([a-z]{1,20})/$', views.html_list, name = 'html_list'),
#                       (r'^json_list/([a-z]{1,20})/$', cache_page(60*15)('json_list')),
                       url(r'^json_list/([a-z]{1,20})/$', views.json_list, name = 'json_list'),
                       url(r'^selectSpecie2', views.selectSpecie2),
                       url(r'^selectSpecie', views.selectSpecie),
                       url(r'^catalog/(\d{1,5})/$', views.catalog, name = 'catalog'),
                       url(r'^catalog', views.catalog, name = 'catalog'),
                       url(r'^showResults', views.showResults),
                       url(r'^ajaxRequest', views.ajaxRequest),
                       url(r'^downloadData', views.download_data),
#                       (r'^xsams2html', 'xsams2html'),
                       url(r'^tools', views.tools, name = 'tools'),
                       url(r'^general', views.general, name = 'general'),
                       url(r'^contact', views.contact, name = 'contact'),
                       url(r'^help', views.help, name = 'help'),
                       url(r'^overview$', views.specieslist, name = 'overview'),
              #         (r'^molecules', 'molecule'),                       
              #         (r'^species/(\d{1,5})/$', 'specie'),
                       url(r'^getfile/(\d{1,5})/$', views.getfile),
                       url(r'^cdms_lite', views.cdms_lite_download),
                       url(r'^recommendation/list/$', views.recommendation_list),
                       url(r'^recommendation/(\d{1,5})/$', views.is_recommended),
                       url(r'^recommendation/XCDMS-(\d{1,5})/$', views.is_recommended),
                       url(r'^recommendation/XJPL-(\d{1,5})/$', views.is_recommended),
              #         (r'^references', 'referencelist'),                       
              #         (r'^filters/(\d{1,5})/$', 'filters'),                      
                       url(r'^login/$',  login, {'template_name': 'cdmsadmin/login.html'}),
                       url(r'^accounts/logout/$', logout, {'template_name': 'cdmsadmin/login.html'}), 
]
