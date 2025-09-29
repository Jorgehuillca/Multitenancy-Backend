from django.urls import path
from .views.appointment import AppointmentViewSet
from .views.appointment_status import AppointmentStatusViewSet
from .views.ticket import TicketViewSet

app_name = 'appointments_status'

urlpatterns = [
    # Endpoints para Appointments
    path('appointments/', AppointmentViewSet.as_view({'get': 'list'}), name='appointment-list'),
    path('appointments/create/', AppointmentViewSet.as_view({'post': 'create'}), name='appointment-create'),
    path('appointments/<int:pk>/', AppointmentViewSet.as_view({'get': 'retrieve'}), name='appointment-detail'),
    path('appointments/<int:pk>/edit/', AppointmentViewSet.as_view({'put': 'update', 'patch': 'partial_update'}), name='appointment-edit'),
    path('appointments/<int:pk>/delete/', AppointmentViewSet.as_view({'delete': 'destroy'}), name='appointment-delete'),
    
    # Custom actions para Appointments
    path('appointments/completed/', AppointmentViewSet.as_view({'get': 'completed'}), name='appointment-completed'),
    path('appointments/pending/', AppointmentViewSet.as_view({'get': 'pending'}), name='appointment-pending'),
    path('appointments/by_date_range/', AppointmentViewSet.as_view({'get': 'by_date_range'}), name='appointment-by-date-range'),
    path('appointments/check_availability/', AppointmentViewSet.as_view({'get': 'check_availability'}), name='appointment-check-availability'),
    path('appointments/<int:pk>/cancel/', AppointmentViewSet.as_view({'post': 'cancel'}), name='appointment-cancel'),
    path('appointments/<int:pk>/reschedule/', AppointmentViewSet.as_view({'post': 'reschedule'}), name='appointment-reschedule'),
    
    # Endpoints para Appointment Statuses (globales)
    path('appointment-statuses/', AppointmentStatusViewSet.as_view({'get': 'list'}), name='appointment-status-list'),
    path('appointment-statuses/create/', AppointmentStatusViewSet.as_view({'post': 'create'}), name='appointment-status-create'),
    path('appointment-statuses/<int:pk>/', AppointmentStatusViewSet.as_view({'get': 'retrieve'}), name='appointment-status-detail'),
    path('appointment-statuses/<int:pk>/edit/', AppointmentStatusViewSet.as_view({'put': 'update', 'patch': 'partial_update'}), name='appointment-status-edit'),
    path('appointment-statuses/<int:pk>/delete/', AppointmentStatusViewSet.as_view({'delete': 'destroy'}), name='appointment-status-delete'),
    
    # Custom actions para Appointment Statuses
    path('appointment-statuses/active/', AppointmentStatusViewSet.as_view({'get': 'active'}), name='appointment-status-active'),
    path('appointment-statuses/<int:pk>/activate/', AppointmentStatusViewSet.as_view({'post': 'activate'}), name='appointment-status-activate'),
    path('appointment-statuses/<int:pk>/deactivate/', AppointmentStatusViewSet.as_view({'post': 'deactivate'}), name='appointment-status-deactivate'),
    path('appointment-statuses/<int:pk>/appointments/', AppointmentStatusViewSet.as_view({'get': 'appointments'}), name='appointment-status-appointments'),
    
    # Endpoints para Tickets
    path('tickets/', TicketViewSet.as_view({'get': 'list'}), name='ticket-list'),
    path('tickets/create/', TicketViewSet.as_view({'post': 'create'}), name='ticket-create'),
    path('tickets/<int:pk>/', TicketViewSet.as_view({'get': 'retrieve'}), name='ticket-detail'),
    path('tickets/<int:pk>/edit/', TicketViewSet.as_view({'put': 'update', 'patch': 'partial_update'}), name='ticket-edit'),
    path('tickets/<int:pk>/delete/', TicketViewSet.as_view({'delete': 'destroy'}), name='ticket-delete'),
    
    # Custom actions para Tickets
    path('tickets/paid/', TicketViewSet.as_view({'get': 'paid'}), name='ticket-paid'),
    path('tickets/pending/', TicketViewSet.as_view({'get': 'pending'}), name='ticket-pending'),
    path('tickets/cancelled/', TicketViewSet.as_view({'get': 'cancelled'}), name='ticket-cancelled'),
    path('tickets/<int:pk>/mark_as_paid/', TicketViewSet.as_view({'post': 'mark_as_paid'}), name='ticket-mark-paid'),
    path('tickets/<int:pk>/mark_paid/', TicketViewSet.as_view({'post': 'mark_paid'}), name='ticket-mark-paid-alias'),
    path('tickets/<int:pk>/mark_as_cancelled/', TicketViewSet.as_view({'post': 'mark_as_cancelled'}), name='ticket-mark-cancelled'),
    path('tickets/<int:pk>/cancel/', TicketViewSet.as_view({'post': 'cancel'}), name='ticket-cancel'),
    path('tickets/by_payment_method/', TicketViewSet.as_view({'get': 'by_payment_method'}), name='ticket-by-payment-method'),
    path('tickets/by_ticket_number/', TicketViewSet.as_view({'get': 'by_ticket_number'}), name='ticket-by-ticket-number'),
    path('tickets/by_number/', TicketViewSet.as_view({'get': 'by_number'}), name='ticket-by-number'),
    path('tickets/statistics/', TicketViewSet.as_view({'get': 'statistics'}), name='ticket-statistics'),
]
