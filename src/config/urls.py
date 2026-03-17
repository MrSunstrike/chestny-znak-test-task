from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.orders.views import orders_root_redirect

urlpatterns = [
    path("", orders_root_redirect, name="root"),
    path("admin/", admin.site.urls),
    path("orders/", include("apps.orders.urls")),
    path("users/", include("apps.users.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
