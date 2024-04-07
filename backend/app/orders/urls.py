from rest_framework.urls import path

from . import views

urlpatterns = [
    path("", views.OrderListView.as_view(), name="order-list"),
    path("<int:order_id>/", views.OrderDetailView.as_view(), name="order-detail"),
]
