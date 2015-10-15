from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.login, name='login'),
    url(r'^register$', views.register, name='register'),
    url(r'^account$', views.account, name='account'),
    url(r'^inventory$', views.inventory, name='inventory'),
    url(r'^app\.css$', views.css, name='css'),
    url(r'.*', views.error404, name='error404'),
]