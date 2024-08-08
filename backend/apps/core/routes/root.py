from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView

from apps.core.controllers.health import health_test

urlpatterns = [
    path('health_test/', health_test),
    path('admin/', admin.site.urls),

    # API
    path('api/v1/', include('apps.core.routes.api')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += (path('endpoints/', include('apps.endpoints.urls')),)
urlpatterns.append(re_path(r'^.*$', TemplateView.as_view(template_name='index.html')))
urlpatterns.append(path('', TemplateView.as_view(template_name='index.html'), name='main'))
