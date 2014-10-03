from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'media_dump.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^search/', views.search),
    url(r'^tree/', views.tree),
    url(r'^suggest/', views.suggest),
    url(r'^$', views.index),
    
    url(r'^test/', views.test),
)