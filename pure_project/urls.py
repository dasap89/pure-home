"""pure_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
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
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from pure.views import IndexPage, SearchPage, CatalogPage

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    
    
    url(r'^api/v2/', include('fiber.rest_api.urls')),
    url(r'^admin/fiber/', include('fiber.admin_urls')),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {'packages': ('fiber',),}),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT,}),
    
    url(r'helpdesk/', include('helpdesk.urls')), # It is needed for helpdesk
    
    url(r'^$', IndexPage.as_view()),  # this should always be placed last
    
    url(r'search/', SearchPage.as_view()),
    
    url(r'catalog/$', CatalogPage.as_view()),

    url(r'catalog/\w+/$', CatalogPage.as_view()),
    
    url(r'', 'fiber.views.page'),
]

# Fix for show static on dev env
# if settings.DEBUG:
#    urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + urlpatterns
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
