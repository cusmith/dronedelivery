from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.hashers import make_password

from decimal import *
from datetime import datetime

from app.models import UserProfile, InvoiceItem, Invoice, Drone, InventoryType
from app.forms import UserForm, UserExtraForm

from json import dumps


def index(request):
	pending_invoice_items = InvoiceItem.objects.filter(invoice__status='pending')
	context = {'pending_invoice_items': pending_invoice_items}
	return render(request, 'app/index.html', context)

def login(request):
	# Should check for existing login and redirect to account page if found

	if request.method == 'POST':

		data = request.POST
		username = data['username']
		password = data['password']

		user = authenticate(username=username,password=password)
		if user is not None:
			if user.is_active:
				auth_login(request,user)
				
				response = HttpResponse()
				response.status_code = 303
				response['location'] = 'account'
				return response

			else:
				print("non-active user")
		else:
			print('incorrect login')



		

	return render(request, 'app/login.html', {})

def register(request):
	# Should check for existing login and prompt for logout if found

	#context = RequestContext(request)

	registered = False

	if request.method == 'POST':

		data = request.POST

		username = data['username']
		password = data['password']
		email = data['email']
		address1 = data['address1']
		address2 = data['address2']
		ccn = data['ccn']
		ccnexp = datetime.strptime(data['ccnexp'],'%Y-%m')

		user = User(username=username,password=password,email=email)
		user.save()
		user.set_password(user.password)
		user.save()

		extra = UserProfile(address1=address1,address2=address2,ccn=ccn, ccnexp=ccnexp)
		extra.user = user
		extra.save()

		user = authenticate(username=username,password=password)
		if user is not None:
			if user.is_active:
				auth_login(request,user)
				
				response = HttpResponse()
				response.status_code = 303
				response['location'] = 'account'
				return response

			else:
				print("non-active user")
		else:
			print('incorrect login')

	return render(request, 'app/register.html', {})

def account(request):
	if request.user.is_authenticated():
		print("authenticated")
	else:
		print("not authenticated")
	return render(request, 'app/account.html', {})

@login_required
def checkout(request):
	# TODO: integrate with database
	#
	#	- Identify the pending invoice belonging to the current user
	#	- Collect list of InvoiceItems associated with that invoice
	#
	#todo request.user when the django user model is implemented
	#userid = request.user
	userid = 1
	try:
		user_invoice = Invoice.objects.filter(status='pending').get(user=userid)
	except Invoice.DoesNotExist:
		#there is no invoice for this user
		user_invoice = None

	if request.method == 'POST':
		response = HttpResponse()
		response.status_code = 303
		response['location'] = 'checkout'
		if request.POST['submit'] == 'confirm order':
			#change this to the delivering state
			if user_invoice is not None:
				user_invoice.status = 'delivering'
				user_invoice.save()
			#redirect away from the checkout page
			response['location'] = 'status'
		elif request.POST['submit'] == 'update quantities':
			#for each item update the count
			if user_invoice is not None:
				invoice_items = InvoiceItem.objects.filter(invoice=user_invoice)
				invoice_types = invoice_items.distinct('inventory_type')
				for intype in invoice_types:
					#The POST has a field 'product-name-marked="on"' for each type to be removed
					# construct the string to lookup and get it from the POST. If it is not present
					# in the POST then assume this type is not to be removed
					quantity_str = (intype.inventory_type.product_name).lower().replace(' ','-') + "-quantity"
					new_count = int(request.POST[quantity_str])
					items = invoice_items.filter(inventory_type=intype.inventory_type)
					count = items.count()
					if new_count > count:
						#todo Get appropriate drone
						newDrone = Drone(status='Idle', location='home')
						newDrone.save()

						#adding items of this type
						for i in range(new_count - count):
							inv_item = InvoiceItem(invoice=user_invoice, 
										drone=newDrone, 
										inventory_type=intype.inventory_type)
							inv_item.save()
						intype.inventory_type.stock_count -= (new_count - count)
						intype.inventory_type.save()
						pass
					elif new_count < count:
						#removing items of this type
						pass
					else:
						#count is not changed
						pass
		elif request.POST['submit'] == 'remove selected':
			#for each item, if it is marked then remove from invoice
			if user_invoice is not None:
				invoice_items = InvoiceItem.objects.filter(invoice=user_invoice)
				invoice_types = invoice_items.distinct('inventory_type')
				for intype in invoice_types:
					#The POST has a field 'product-name-marked="on"' for each type to be removed
					# construct the string to lookup and get it from the POST. If it is not present
					# in the POST then assume this type is not to be removed
					mark_str = (intype.inventory_type.product_name).lower().replace(' ','-') + "-marked"
					removal = request.POST.get(mark_str, 'off')
					if removal == 'on':
						items = invoice_items.filter(inventory_type=intype.inventory_type)
						#readd count to existing stock
						count = items.count()
						intype.inventory_type.stock_count += count
						intype.inventory_type.save()
						#remove these items
						items.delete()
		else:
			#unknown post
			print 'Unknown POST submit: ' + request.POST['submit']
			pass

		return response
	
	subtotal = Decimal(0.0)
	real_cart = []
	if user_invoice is not None:
		invoice_items = InvoiceItem.objects.filter(invoice=user_invoice)
		invoice_types = invoice_items.distinct('inventory_type')
		for intype in invoice_types:
			#get the count of items ordered
			count = invoice_items.filter(inventory_type=intype.inventory_type).count()
			#get the item description
			inventory_obj = InventoryType.objects.get(id=intype.inventory_type.id)
			#display in cart
			real_cart.append(type('',(object,),{'type': inventory_obj,'count': count})())
			#add price to subtotal
			subtotal += Decimal(count) * inventory_obj.price
	
	tax = (subtotal * Decimal(0.09)).quantize(Decimal('0.01'), rounding=ROUND_UP)
	total = subtotal + tax
	context = {'cart_items': real_cart, 'subtotal': subtotal, 'tax':tax, 'total':total}
	return render(request, 'app/checkout.html', context)

def status(request):

	if 'invoice' not in request.GET:
		return error404(request)

	invoice_id = request.GET['invoice']

	invoice = Invoice.objects.filter(id=invoice_id)

	if len(invoice) == 0:
		return error404(request)

	if 'action' in request.GET:
		if request.GET['action'] == 'update':
	
			drones = Drone.objects.all().filter(invoiceitem__invoice=invoice_id).distinct()

			response = HttpResponse(content_type='application/json')
			response.write(dumps(sum(map(lambda drone: [drone],drones.values()),[])))
			return response

	context = {
		'invoice_id': invoice_id
	}
	return render(request, 'app/status.html', context)

@login_required
def inventory(request):
	if request.method == 'POST':
		#todo request.user when the django user model is implemented
		#userid = request.user
		userid = 1

		#get the pending invoice for this user.
		# if one doesn't exist then create a new one
		try:
			user_invoice = Invoice.objects.filter(status='pending').get(user=userid)
		except Invoice.DoesNotExist:
			try:
				user_invoice = Invoice(status='pending', user=User.objects.get(id=userid))
				user_invoice.save()
			except ValueError:
				#user doesn't exist - shouldn't happen when user implemented
				response = HttpResponse()
				response.status_code = 303
				response['location'] = 'login'
				return response
				

		inventoryItem = InventoryType.objects.get(product_name=request.POST['item'])
		
		#todo get appropriate drone
		newDrone = Drone(status='Idle', location='home')
		newDrone.save()
		
		itemCount = int(request.POST['quantity'])
		#add invoice items to the invoice with the drone
		for x in range(itemCount):
			inv_item = InvoiceItem(invoice=user_invoice, 
						drone=newDrone, 
						inventory_type=inventoryItem)
			inv_item.save()
		
		#update the inventory count
		inventoryItem.stock_count = inventoryItem.stock_count - itemCount
		inventoryItem.save()
		
		response = HttpResponse()
		response.status_code = 303
		if request.POST['submit'] == 'add and go to checkout':
			response['location'] = 'checkout'
		else:
			response['location'] = 'inventory'
		return response
	
	inventory_items = InventoryType.objects.all()
	context = {'inventory_items': inventory_items}
	return render(request, 'app/inventory.html', context)

def history(request):
	# Use this line once users get implemented
	# invoices = Invoice.objects.filter(status='complete', user=request.user)
	invoices = Invoice.objects.all()
	context = {'invoices': invoices}
	print(context)
	return render(request, 'app/history.html', context)

def css(request):
	return render(request, request.path[1:], {},content_type='text/css')

def error404(request):
	return render(request, 'app/error404.html', {'pagepath':request.path})
