from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
admin.autodiscover()

urlpatterns = [
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

    url(r'^newsletter/', include('pennyblack.urls'), name='pennyblack'),
]
