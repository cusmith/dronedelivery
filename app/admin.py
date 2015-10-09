from django.contrib import admin

from app.models import User, Invoice, Drone, InventoryType, InvoiceItem
# Register your models here.
admin.site.register(User)
admin.site.register(Invoice)
admin.site.register(Drone)
admin.site.register(InventoryType)
admin.site.register(InvoiceItem)
