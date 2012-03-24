from django.conf.urls.defaults import patterns, include, url
from course_server import views
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    ('^key/$', views.key),
    ('^course/upload/$', views.upload_courses),
    # Examples:
    # url(r'^$', 'course_server.views.home', name='home'),
    # url(r'^course_server/', include('course_server.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
