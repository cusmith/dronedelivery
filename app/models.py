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

		return serialized_items

	def get_item_type_counts_by_name(self):
		invoice_items = InvoiceItem.objects.filter(invoice=self)
		serialized_items = {}
		for item in invoice_items:
			count = serialized_items.setdefault(item.inventory_type.product_name, 0)
			serialized_items[item.inventory_type.product_name] = count + 1

		return serialized_items

	def confirm_order(self):

		#Get drones for the order 
		drone = Drone.assign_drone()

		invoice_items = InvoiceItem.objects.filter(invoice=self)
		for item in invoice_items:
			item.drone = drone
			item.save()

		#change this invoice to the delivering state
		self.status = Invoice.STATUS_DELIVERING
		self.save()
		return

	#Remove some number of the specified type
	#Expects: itype - the type of item to be removed
	#	  remove_count - the number of items to remove
	def remove_type(self, itype, remove_count):
		if remove_count > 0:
			try:
				items = InvoiceItem.objects.filter(invoice=self).filter(inventory_type=itype)
			except:
				#no matching items
				return
			if remove_count > items.count():
				#remove all the items
				remove_count = items.count()
			
			#delete some or all of the items
			for x in range(remove_count):
				items[0].delete()
			
			#re-add count to existing stock
			itype.stock_count += remove_count
			itype.save()
		else:
			#not removing anything
			pass
		return

	def complete_invoice(self):
		items = InvoiceItem.objects.filter(invoice=self)
		for item in items:
			if item.drone.status == Drone.STATUS_DELIVERING:
				item.drone.status = Drone.STATUS_IDLE
				item.drone.save()

		self.status = Invoice.STATUS_COMPLETE
		self.save()
		return

	@staticmethod
	def get_cart_invoice(user):
		pending_invoices = Invoice.objects.filter(user=user, status=Invoice.STATUS_PENDING)

		if len(pending_invoices) > 1:
			# There should only ever be 1 pending invoice, ***handle this error case better***
			return None

		elif len(pending_invoices) == 0:
			cart_invoice = Invoice.objects.create(user=user, status=Invoice.STATUS_PENDING)
		else:
			cart_invoice = pending_invoices[0]

		return cart_invoice

class Drone(models.Model):
	HOME = '48.463101, -123.313743'

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

	@staticmethod
	def assign_drone():
		available_drones = Drone.objects.filter(status=Drone.STATUS_IDLE)
		if available_drones:
			assign_drone = available_drones[0]
			assign_drone.status = Drone.STATUS_DELIVERING
			assign_drone.save()
		else:
			assign_drone = Drone(status=Drone.STATUS_IDLE, location=Drone.HOME)
			assign_drone.save()
		return assign_drone

class InventoryType(models.Model):
	product_name = models.CharField(max_length=50)
	stock_count = models.IntegerField(default=0)
	description = models.CharField(max_length=200)
	price = models.DecimalField(max_digits=8, decimal_places=2)

	def __unicode__(self):
		return '%d:%s' % (self.id, self.product_name)

class InvoiceItem(models.Model):
	invoice = models.ForeignKey(Invoice)
	drone = models.ForeignKey(Drone, null=True)
	inventory_type = models.ForeignKey(InventoryType)

	def __unicode__(self):
		return '%d:%s' % (self.id, self.inventory_type.product_name)
