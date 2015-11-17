from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.hashers import make_password

from datetime import datetime

from app.models import UserProfile, InvoiceItem, Invoice, Drone, InventoryType
from app.forms import UserForm, UserExtraForm

from json import dumps

# Homepage
###########

def index(request):
	pending_invoice_items = InvoiceItem.objects.filter(invoice__status='pending')
	context = {'pending_invoice_items': pending_invoice_items}
	return render(request, 'app/index.html', context)

# Account Management
#####################

# Load the My Account Page
def account(request):
	if request.user.is_authenticated():
		print("authenticated")
	else:
		print("not authenticated")
	return render(request, 'app/account.html', {})

# Load the Login Page (or redirect to My Account if logged in)
def login(request):
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

# Register a new user
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

# Purchases (All require login)
############

# Load Checkout Page
@login_required
def checkout(request):
	# TODO: integrate with database
	#
	#	- Identify the pending invoice belonging to the current user
	#	- Collect list of InvoiceItems associated with that invoice
	#
	cart_invoice = Invoice.get_cart_invoice(request.user)

	if request.method == 'GET':

		cart_items = cart_invoice.get_item_type_counts()

		cart = []
		for itype, count in cart_items.iteritems():
			cart.append(type('',(object,),{'type': itype,'count': count})())
		context = {'cart_items': cart}
		return render(request, 'app/checkout.html', context)

	elif request.method == 'POST':
		cart_invoice.status = 'delivering'
		cart_invoice.save()

		return render(request, 'app/account.html', {})

# Load Purchase History
@login_required
def history(request):
	# Use this line once users get implemented
	# invoices = Invoice.objects.filter(status='complete', user=request.user)
	invoices = Invoice.objects.filter(user=request.user, status='completed')
	context = {'invoices': invoices}
	return render(request, 'app/history.html', context)

# Load App Inventory Page (for adding to cart)
@login_required
def inventory(request):
	if request.method == 'POST':
		#get the pending invoice for this user.
		# if one doesn't exist then create a new one
		user_invoice = Invoice.get_cart_invoice(request.user)

		if not user_invoice:
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

# Load Order Status Page
@login_required
def status(request):
	if request.method == 'GET':
		invoices = Invoice.objects.filter(user=request.user, status='delivering')
		context = {'invoices': invoices}
		return render(request, 'app/status.html', context)
	elif request.method == 'POST':
		invoice_id = int(request.POST['invoice_id'])
		# Set invoice to completed, reload the page
		return render(request, 'app/status.html', context)
# Other
########

# 404 Page
def error404(request):
	return render(request, 'app/error404.html', {'pagepath':request.path})

# CSS
def css(request):
	return render(request, request.path[1:], {},content_type='text/css')