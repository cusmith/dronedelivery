from django.conf.urls import url

from . import views

urlpatterns = [
    # Homepage
    url(r'^$', views.index, name='index'),

    # Account Management
    url(r'^account$', views.account, name='account'),
    url(r'^login$', views.login, name='login'),
    url(r'^register$', views.register, name='register'),
    
    # Purchases
    url(r'^checkout$', views.checkout, name='checkout'),
    url(r'^history$', views.history, name='history'),
    url(r'^inventory$', views.inventory, name='inventory'),
    url(r'^status$', views.status, name='status'),

    # CSS
    url(r'^app\.css$', views.css, name='css'),

    # 404
    url(r'.*', views.error404, name='error404'),
    
]
