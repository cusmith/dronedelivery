from django.conf.urls import url

from . import views

urlpatterns = [
    # Homepage
    url(r'^$', views.index, name='index'),

    # Account Management
    url(r'^account$', views.account, name='account'),
    url(r'^login$', views.login, name='login'),
    url(r'^register$', views.register, name='register'),
    url(r'^deleteAccount$', views.deleteAccount, name='deleteAccount'),
    url(r'^logoutUser$', views.logoutUser, name='logoutUser'),
    
    # Purchases
    url(r'^checkout$', views.checkout, name='checkout'),
    url(r'^history$', views.history, name='history'),
    url(r'^inventory$', views.inventory, name='inventory'),
    url(r'^status$', views.status, name='status'),
    url(r'^details$', views.details, name='details'),
    url(r'^details/(?P<invoice>[0-9]+)/$', views.details, name='details'),

    # 404
    url(r'.*', views.error404, name='error404'),
    
]
