from django.db import models
from django.db.models import Count
from django.contrib.auth.models import User
from datetime import datetime

class UserProfile(models.Model):
	user = models.OneToOneField(User)

	address1 = models.CharField(max_length=100)
	address2 = models.CharField(max_length=100)
	ccn = models.CharField(max_length=16)
	ccnexp = models.DateField()

	def __unicode__(self):
		return self.user.username

class Invoice(models.Model):
	STATUS_PENDING = 'pending' # IN CART INVOICE, Can only have 1 pending invoice at a time.
	STATUS_DELIVERING = 'delivering' # Once a cart purchase is confirmed, set to delivering.
	STATUS_COMPLETE = 'complete' # Not sure when to set to complete, need to make some logic?

	STATUS_CHOICES = (
		(STATUS_PENDING, 'Pending'),
		(STATUS_DELIVERING, 'Delivering'),
		(STATUS_COMPLETE, 'Complete')
	)

	status = models.CharField(max_length=20, choices=STATUS_CHOICES)
	user = models.ForeignKey(User)

	def __unicode__(self):
		return '%d:%s' % (self.id, self.user)

	def get_item_type_counts(self):
		invoice_items = InvoiceItem.objects.filter(invoice=self)
		serialized_items = {}
		for item in invoice_items:
			count = serialized_items.setdefault(item.inventory_type, 0)
			serialized_items[item.inventory_type] = count + 1

		print serialized_items
		return serialized_items

	@staticmethod
	def get_cart_invoice(user):
		pending_invoices = Invoice.objects.filter(user=user, status='pending')

		if len(pending_invoices) > 1:
			# There should only ever be 1 pending invoice, ***handle this error case better***
			return None

		elif len(pending_invoices) == 0:
			cart_invoice = Invoice.objects.create(user=user, status='pending')
		else:
			cart_invoice = pending_invoices[0]

		return cart_invoice

class Drone(models.Model):
	STATUS_IDLE = 'idle'
	STATUS_DELIVERING = 'delivering'
	STATUS_RETURNING = 'returning'
	STATUS_MAINTENANCE = 'maintenance'

	STATUS_CHOICES = (
		(STATUS_IDLE, 'Idle'),
		(STATUS_DELIVERING, 'Delivering'),
		(STATUS_RETURNING, 'Returning'),
		(STATUS_MAINTENANCE, 'Maintenance')
	)

	status = models.CharField(max_length=20, choices=STATUS_CHOICES)
	location = models.CharField(max_length=50)

	def __unicode__(self):
		return '%d:%s' % (self.id, self.status)

class InventoryType(models.Model):
	product_name = models.CharField(max_length=50)
	stock_count = models.IntegerField(default=0)
	description = models.CharField(max_length=200)
	price = models.DecimalField(max_digits=8, decimal_places=2)

	def __unicode__(self):
		return '%d:%s' % (self.id, self.product_name)

class InvoiceItem(models.Model):
	invoice = models.ForeignKey(Invoice)
	drone = models.ForeignKey(Drone)
	inventory_type = models.ForeignKey(InventoryType)

	def __unicode__(self):
		return '%d:%s' % (self.id, self.inventory_type.product_name)
