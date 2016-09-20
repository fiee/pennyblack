from django.conf.urls import url
from pennyblack import views

urlpatterns = [
    url(r'^link/(?P<mail_hash>[^/]+)/(?P<link_hash>[a-z0-9]+)/$',
        views.redirect_link,
        name='pennyblack.redirect_link'),
    url(r'^proxy/(?P<mail_hash>[^/]+)/(?P<link_hash>[a-z0-9]+)/$',
        views.proxy,
        name='pennyblack.proxy'),
    url(r'^view/mail/(?P<mail_hash>\w+)',
        views.view,
        name='pennyblack.view'),
    url(r'^view/(?P<job_slug>[\w-]+)/',
        views.view_public,
        name='pennyblack.view_public'),
    url(r'^ping/(?P<mail_hash>\w*)/(?P<filename>.*)$',
        views.ping,
        name='pennyblack.ping'),
]
