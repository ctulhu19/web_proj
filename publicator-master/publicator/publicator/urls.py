"""publicator URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('publications/', include('publications.urls'))
"""
from django.contrib import admin
from django.views.generic.edit import CreateView
from django.urls import include, path, reverse_lazy
from publications.forms import AuthorForm
from django.conf.urls.static import static
from django.conf import settings

handler404 = "pages.views.page_not_found"
handler500 = "pages.views.page_internal_server_error"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('publications.urls')),
    path('pages/', include('pages.urls')),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=AuthorForm,
            success_url=reverse_lazy('publications:index'),
        ),
        name='registration',
    ),
    path('auth/', include('django.contrib.auth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

