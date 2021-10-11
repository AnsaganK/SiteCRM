from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from django.contrib.auth import views as acc

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path('', include('clarion.urls', namespace='clarion')),
    path('accounts/login/', acc.LoginView.as_view(), name='login'),
    path('accounts/logout/', acc.LogoutView.as_view(), name='logout'),
]

