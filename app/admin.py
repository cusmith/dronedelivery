from django.contrib import admin

from app.models import UserProfile, Invoice, Drone, InventoryType, InvoiceItem

admin.site.register(UserProfile)
admin.site.register(Invoice)
admin.site.register(Drone)
admin.site.register(InventoryType)
admin.site.register(InvoiceItem)
