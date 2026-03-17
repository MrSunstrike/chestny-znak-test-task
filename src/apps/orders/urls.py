from django.urls import path

from apps.orders.views import OrderCreateView, OrderDetailView, OrderListView, users_autocomplete

app_name = "orders"

urlpatterns = [
    path("", OrderListView.as_view(), name="list"),
    path("users-autocomplete/", users_autocomplete, name="users-autocomplete"),
    path("create/", OrderCreateView.as_view(), name="create"),
    path("<int:pk>/", OrderDetailView.as_view(), name="detail"),
]
