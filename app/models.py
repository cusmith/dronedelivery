from django.db import models

# Create your models here.
class User(models.Model):
	username = models.CharField(max_length=50)
	name = models.CharField(max_length=50)
	address = models.CharField(max_length=100)
	email = models.CharField(max_length=50)
	phone_number = models.CharField(max_length=10)

	def __unicode__(self):
		return self.username

class Invoice(models.Model):
	STATUS_PENDING = 'pending'
	STATUS_DELIVERING = 'delivering'
	STATUS_COMPLETE = 'complete'

	STATUS_CHOICES = (
		(STATUS_PENDING, 'Pending'),
		(STATUS_DELIVERING, 'Delivering'),
		(STATUS_COMPLETE, 'Complete')
	)

	status = models.CharField(max_length=20, choices=STATUS_CHOICES)
	user = models.ForeignKey(User)

	def __unicode__(self):
		return '%d:%s' % (self.id, self.user)
	

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