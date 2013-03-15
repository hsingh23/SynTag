from django.conf.urls import patterns, include, url
urlpatterns = patterns('syn.views',
                       url(r'^$', 'home'),
                       )
