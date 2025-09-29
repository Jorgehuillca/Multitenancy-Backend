from django.urls import path
from .views.history import histories_list, history_create, history_update, history_delete
from .views.document_type import document_types_list, document_type_create, document_type_delete, document_type_edit
from .views.payment_type import payment_types_list, payment_type_create, payment_type_delete, payment_type_edit
from .views.payment_status import payment_statuses_list, payment_status_create, payment_status_edit, payment_status_delete
from .views.predetermined_price import predetermined_prices_list, predetermined_price_create, predetermined_price_update, predetermined_price_delete

urlpatterns = [
    # Histories - Estructura estándar
    path("histories/", histories_list, name="histories_list"),
    path("histories/create/", history_create, name="history_create"),
    path("histories/<int:pk>/", histories_list, name="history_detail"),  # Ver historial específico
    path("histories/<int:pk>/edit/", history_update, name="history_edit"),
    path("histories/<int:pk>/delete/", history_delete, name="history_delete"),

    # Document Types - Estructura estándar
    path("document_types/", document_types_list, name="document_types_list"),
    path("document_types/create/", document_type_create, name="document_type_create"),
    path("document_types/<int:pk>/", document_types_list, name="document_type_detail"),  # Ver tipo específico
    path("document_types/<int:pk>/edit/", document_type_edit, name="document_type_edit"),
    path("document_types/<int:pk>/delete/", document_type_delete, name="document_type_delete"),

    # Payment Types - Estructura estándar
    path("payment_types/", payment_types_list, name="payment_types_list"),
    path("payment_types/create/", payment_type_create, name="payment_type_create"),
    path("payment_types/<int:pk>/", payment_types_list, name="payment_type_detail"),  # Ver tipo específico
    path("payment_types/<int:pk>/edit/", payment_type_edit, name="payment_type_edit"),
    path("payment_types/<int:pk>/delete/", payment_type_delete, name="payment_type_delete"),

    # Payment Statuses - Estructura estándar
    path("payment_statuses/", payment_statuses_list, name="payment_statuses_list"),
    path("payment_statuses/create/", payment_status_create, name="payment_status_create"),
    path("payment_statuses/<int:pk>/", payment_statuses_list, name="payment_status_detail"),  # Ver estado específico
    path("payment_statuses/<int:pk>/edit/", payment_status_edit, name="payment_status_edit"),
    path("payment_statuses/<int:pk>/delete/", payment_status_delete, name="payment_status_delete"),

    # Predetermined Prices - Estructura estándar
    path("predetermined_prices/", predetermined_prices_list, name="predetermined_prices_list"),
    path("predetermined_prices/create/", predetermined_price_create, name="predetermined_price_create"),
    path("predetermined_prices/<int:pk>/", predetermined_prices_list, name="predetermined_price_detail"),  # Ver precio específico
    path("predetermined_prices/<int:pk>/edit/", predetermined_price_update, name="predetermined_price_edit"),
    path("predetermined_prices/<int:pk>/delete/", predetermined_price_delete, name="predetermined_price_delete"),
]
