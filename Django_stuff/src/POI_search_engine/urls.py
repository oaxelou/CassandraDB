""" Olympia Axelou, May 2020
 This script is part of the project "A POI search engine using CassandraDB"
 
 In here, all the usrls are defined are associated with a view (from search_engine.views)
"""

"""POI_search_engine URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from search_engine.views import home,search,results, business, insert_review, insert_tip, user
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', home),
    url(r'^search/$', search),
    url(r'^results/$', results),
    url(r'^business/$', business),
    url(r'^insert_review/$', insert_review),
    url(r'^insert_tip/$', insert_tip),
    url(r'^user/$', user),
]
