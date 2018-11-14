from django.conf.urls import url
from cleaning import views

urlpatterns = [
    url(r'^query_phone/$', views.query_phone),
    url(r'^filter_phone_number/$', views.filter_phone_number),
    url(r'^extract_city/$', views.extract_city),
    url(r'^filter_abbreviation/$', views.filter_abbreviation),
    url(r'^filter_company/$', views.filter_company),
    url(r'scale_clean/$', views.scale_clean),
    url(r'info_clean/$', views.info_clean),
    url(r'match_company/$', views.match_company),
    url(r'info_contain/$', views.info_contain),
]

