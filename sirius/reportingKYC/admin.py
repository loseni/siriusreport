from django.contrib import admin

from .models import Base, Agent, Traitement, TypeAlerte, Flag, StatutAlert, TrancheAge, Stock
# Register your models here.
admin.site.register(Base)
admin.site.register(Agent)
admin.site.register(Traitement)
admin.site.register(TypeAlerte)
admin.site.register(Flag)
admin.site.register(StatutAlert)
admin.site.register(TrancheAge)
admin.site.register(Stock)