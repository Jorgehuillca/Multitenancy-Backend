from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction
from .models import Appointment, Ticket
from .services.ticket_service import TicketService

@receiver(post_save, sender=Appointment)
def create_ticket_for_appointment(sender, instance, created, **kwargs):
    """
    Al crear una cita, genera ticket y asigna ticket_number a la cita.
    """
    if not created:
        return

    ticket_service = TicketService()
    ticket_number = ticket_service.generate_ticket_number()  # string

    # Obtener el método de pago del tipo de pago de la cita
    payment_method = 'efectivo'  # Por defecto
    if instance.payment_type:
        payment_method = instance.payment_type.name.lower()
        # Mapear nombres de PaymentType a métodos de pago del ticket
        payment_method_mapping = {
            'efectivo': 'efectivo',
            'tarjeta de debito': 'tarjeta',
            'yape': 'yape',
        }
        payment_method = payment_method_mapping.get(payment_method, payment_method)

    with transaction.atomic():
        Ticket.objects.create(
            appointment=instance,
            ticket_number=ticket_number,
            amount=instance.payment or 0,
            payment_method=payment_method,
            description=f'Ticket generado automáticamente para cita #{instance.id}',
            status='pending',
        )
        # IMPORTANTE: update() para no disparar otro post_save
        Appointment.objects.filter(pk=instance.pk).update(ticket_number=ticket_number)


# Función obsoleta - ahora usa TicketService.generate_ticket_number()
# def generate_unique_ticket_number() -> str:
#     """
#     Ticket legible basado en timestamp + microsegundos (string).
#     18 dígitos aprox. (cómodo para VARCHAR(20)).
#     """
#     now = timezone.now()
#     # Ej: 20250829 163303 123456  -> '20250829163303123456'
#     return f"{now.strftime('%Y%m%d%H%M%S')}{now.microsecond:06d}"


@receiver(post_save, sender=Appointment)
def update_ticket_when_appointment_changes(sender, instance, created, **kwargs):
    """
    Si cambia el pago de la cita, sincroniza el ticket existente.
    """
    if created:
        return
    try:
        ticket = Ticket.objects.get(appointment=instance)
    except Ticket.DoesNotExist:
        # Si por alguna razón no existe, lo creamos sin volver a hacer save() en la cita
        ticket_service = TicketService()
        
        # Obtener el método de pago del tipo de pago de la cita
        payment_method = 'efectivo'  # Por defecto
        if instance.payment_type:
            payment_method = instance.payment_type.name.lower()
            # Mapear nombres de PaymentType a métodos de pago del ticket
            payment_method_mapping = {
                'efectivo': 'efectivo',
                'tarjeta de debito': 'tarjeta',
                'yape': 'yape',
            }
            payment_method = payment_method_mapping.get(payment_method, payment_method)
        
        Ticket.objects.create(
            appointment=instance,
            ticket_number=instance.ticket_number or ticket_service.generate_ticket_number(),
            amount=instance.payment or 0,
            payment_method=payment_method,
            description=f'Ticket autogenerado por sincronización para cita #{instance.id}',
            status='pending',
        )
        return

    # Actualizar amount y payment_method si han cambiado
    needs_update = False
    update_fields = []
    
    if instance.payment is not None and ticket.amount != instance.payment:
        ticket.amount = instance.payment
        update_fields.append('amount')
        needs_update = True
    
    # Actualizar método de pago si el tipo de pago cambió
    if instance.payment_type:
        new_payment_method = instance.payment_type.name.lower()
        payment_method_mapping = {
            'efectivo': 'efectivo',
            'tarjeta de debito': 'tarjeta',
            'yape': 'yape',
        }
        new_payment_method = payment_method_mapping.get(new_payment_method, new_payment_method)
        
        if ticket.payment_method != new_payment_method:
            ticket.payment_method = new_payment_method
            update_fields.append('payment_method')
            needs_update = True
    
    if needs_update:
        update_fields.append('updated_at')
        ticket.save(update_fields=update_fields)