# Optional:
# Use this file to connect views from views.py in the same
# directory to their paths.
from django.contrib.auth.views import LoginView, LogoutView

#from django.conf.paths.defaults import *
from django.urls import path, include, re_path
#from django.conf import settings

#from django.views.decorators.cache import cache_page
from . import views

#
urlpatterns = [
#                       settings.NODENAME+'.node.views',
                       path('', views.index, name = 'index'),
                       path('jpl$', views.index, name ='jpl'),
                       path('home', views.index, name = 'home'),
                       path('queryPage', views.queryPage, name = 'queryPage'),                       
                       path('queryForm', views.query_form, name = 'query_form'), 
                       path('querySpecies', views.queryspecies, name = 'querySpecies'),
                       re_path('html_list/([a-z]{1,20})/$', views.html_list, name = 'html_list'),
#                       (r'^json_list/([a-z]{1,20})/$', cache_page(60*15)('json_list')),
                       re_path(r'json_list/([a-z]{1,20})/$', views.json_list, name = 'json_list'),
                       path('selectSpecie2', views.selectSpecie2),
                       path('selectSpecie', views.selectSpecie),
                       path('catalog/(\d{1,5})/$', views.catalog, name = 'catalog'),
                       path('catalog', views.catalog, name = 'catalog'),
                       path('showResults', views.showResults),
                       path('ajaxRequest', views.ajaxRequest),
                       path('downloadData', views.download_data),
#                       (r'^xsams2html', 'xsams2html'),
                       path('tools', views.tools, name = 'tools'),
                       path('general', views.general, name = 'general'),
                       path('contact', views.contact, name = 'contact'),
                       path('help', views.help, name = 'help'),
                       path('overview$', views.specieslist, name = 'overview'),
              #         (r'^molecules', 'molecule'),                       
              #         (r'^species/(\d{1,5})/$', 'specie'),
                       re_path('getfile/(\d{1,5})/$', views.getfile),
                       path('cdms_lite', views.cdms_lite_download),
                       path('recommendation/list/$', views.recommendation_list),
                       path('recommendation/(\d{1,5})/$', views.is_recommended),
                       path('recommendation/XCDMS-(\d{1,5})/$', views.is_recommended),
                       path('recommendation/XJPL-(\d{1,5})/$', views.is_recommended),
              #         (r'^references', 'referencelist'),                       
              #         (r'^filters/(\d{1,5})/$', 'filters'),                      
 #                      path(r'^login/$',  login, {'template_name': 'cdmsadmin/login.html'}),
                       
                       path('accounts/logout/$', LogoutView.as_view(template_name= 'cdmsadmin/login.html')), 
]
