from django.db.models import Count, Sum, Avg, Q, Case, When, F, Value
from django.db.models.functions import ExtractWeekDay, Concat
from appointments_status.models.appointment import Appointment
from appointments_status.models.appointment_status import AppointmentStatus
from architect.utils.tenant import filter_by_tenant, get_tenant, is_global_admin

class StatisticsService:
    def get_metricas_principales(self, start, end, user=None):
        qs = Appointment.objects.filter(
            appointment_date__date__range=[start, end]
        )
        
        # Aplicar filtrado por tenant si se proporciona usuario
        if user:
            qs = filter_by_tenant(qs, user, field='reflexo')
        
        return qs.aggregate(
            ttlpacientes=Count("patient", distinct=True),
            ttlsesiones=Count("id"),
            ttlganancias=Sum("payment")
        )

    def get_tipos_de_pago(self, start, end, user=None):
        qs = Appointment.objects.filter(
            appointment_date__date__range=[start, end]
        )
        
        # Aplicar filtrado por tenant si se proporciona usuario
        if user:
            qs = filter_by_tenant(qs, user, field='reflexo')
        
        pagos = qs.values("payment_type__name").annotate(usos=Count("id"))
        return {(p["payment_type__name"] or "Sin tipo"): p["usos"] for p in pagos}

    def get_rendimiento_terapeutas(self, start, end, user=None):
        # 1. Consulta base: sesiones e ingresos por terapeuta 
        qs = Appointment.objects.filter(
            appointment_date__date__range=[start, end]
        )
        
        # Aplicar filtrado por tenant si se proporciona usuario
        if user:
            qs = filter_by_tenant(qs, user, field='reflexo')
        
        stats = list(qs.values("therapist__id").annotate(
            # Formato de nombre  "Apellido1 Apellido2, Nombre"
            terapeuta=Concat(
                'therapist__last_name_paternal',
                Value(' '),
                'therapist__last_name_maternal', 
                Value(', '),
                'therapist__first_name'
            ),
            sesiones=Count("id"),
            ingresos=Sum("payment")
        ))
        
        if not stats:
            return []
        
        # 2. Calculamos promedios globales (evitar división por cero)
        total_sesiones = sum(s['sesiones'] for s in stats)
        total_ingresos = sum(float(s['ingresos'] or 0) for s in stats)  
        num_terapeutas = len(stats)
        
        prom_sesiones = (total_sesiones / num_terapeutas) if num_terapeutas > 0 else 1
        prom_ingresos = (total_ingresos / num_terapeutas) if num_terapeutas > 0 else 1
        # Si el promedio resultó 0 (p.ej., no hubo sesiones/ingresos en el rango), usar 1 para evitar división por cero
        prom_sesiones = prom_sesiones if prom_sesiones > 0 else 1
        prom_ingresos = prom_ingresos if prom_ingresos > 0 else 1
        
        # 3. Calcular rating original para cada terapeuta
        for stat in stats:
            sesiones = stat['sesiones']
            ingresos = float(stat['ingresos'] or 0)  
            
            # Fórmula 70% sesiones, 30% ingresos
            rating_original = (sesiones / prom_sesiones) * 0.7 + (ingresos / prom_ingresos) * 0.3
            stat['raiting_original'] = rating_original
        
        # 4. Encontrar el máximo rating original (evitar división por cero al escalar)
        max_original = max((s['raiting_original'] for s in stats), default=1)
        if max_original <= 0:
            max_original = 1
        
        # 5. Escalar a 5 puntos y formatear resultado
        resultado = []
        for stat in stats:
            scaled_rating = (stat['raiting_original'] / max_original) * 5
            
            resultado.append({
                "id": stat["therapist__id"],
                "terapeuta": stat['terapeuta'] or "Sin nombre",   
                "sesiones": stat["sesiones"],
                "ingresos": float(stat["ingresos"]) if stat["ingresos"] else 0.0,
                "raiting": round(scaled_rating, 2) 
            })
        
        return resultado

    def get_ingresos_por_dia_semana(self, start, end, user=None):
        
        dias_semana = {
            1: "Domingo",       
            2: "Lunes",      
            3: "Martes",     
            4: "Miercoles",   
            5: "Jueves",    
            6: "Viernes",      
            7: "Sabado"     
        }
        
        qs = Appointment.objects.filter(
            appointment_date__date__range=[start, end]
        )
        
        # Aplicar filtrado por tenant si se proporciona usuario
        if user:
            qs = filter_by_tenant(qs, user, field='reflexo')
        
        ingresos_raw = qs.annotate(dia_semana=ExtractWeekDay("appointment_date")).values("dia_semana").annotate(total=Sum("payment")).order_by("dia_semana")
        
        
        resultado = {}
        for item in ingresos_raw:
            dia_nombre = dias_semana.get(item["dia_semana"], f"Día {item['dia_semana']}")
            resultado[dia_nombre] = float(item["total"]) if item["total"] else 0.0
        
        return resultado

    def get_sesiones_por_dia_semana(self, start, end, user=None):
        dias_semana = {
            1: "Domingo", 2: "Lunes", 3: "Martes", 4: "Miercoles",
            5: "Jueves", 6: "Viernes", 7: "Sabado"
        }
        
        qs = Appointment.objects.filter(
            appointment_date__date__range=[start, end]
        )
        
        # Aplicar filtrado por tenant si se proporciona usuario
        if user:
            qs = filter_by_tenant(qs, user, field='reflexo')
        
        sesiones_raw = qs.annotate(dia_semana=ExtractWeekDay("appointment_date")).values("dia_semana").annotate(sesiones=Count("id")).order_by("dia_semana")
        
        resultado = {}
        for item in sesiones_raw:
            dia_nombre = dias_semana.get(item["dia_semana"], f"Día {item['dia_semana']}")
            resultado[dia_nombre] = item["sesiones"]
        
        return resultado

    def get_tipos_pacientes(self, start, end, user=None):
        qs = Appointment.objects.filter(
            appointment_date__range=[start, end]
        )
        
        # Aplicar filtrado por tenant si se proporciona usuario
        if user:
            qs = filter_by_tenant(qs, user, field='reflexo')
        
        # appointment_status es ForeignKey → comparar por objeto o por nombre del estado
        status_c = AppointmentStatus.objects.filter(name__iexact="C").first()
        status_cc = AppointmentStatus.objects.filter(name__iexact="CC").first()

        return qs.aggregate(
            c=Count("id", filter=Q(appointment_status=status_c) if status_c else Q(pk__isnull=True)),
            cc=Count("id", filter=Q(appointment_status=status_cc) if status_cc else Q(pk__isnull=True))
        )

    def get_statistics(self, start, end, user=None):
        return {
            "terapeutas": self.get_rendimiento_terapeutas(start, end, user),
            "tipos_pago": self.get_tipos_de_pago(start, end, user),
            "metricas": self.get_metricas_principales(start, end, user),
            "ingresos": self.get_ingresos_por_dia_semana(start, end, user),
            "sesiones": self.get_sesiones_por_dia_semana(start, end, user),
            "tipos_pacientes": self.get_tipos_pacientes(start, end, user),
        }