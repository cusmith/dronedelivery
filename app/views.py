from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.hashers import make_password

from decimal import *
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
	loginFailed = False
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
				loginFailed = True
				print("non-active user")
		else:
			loginFailed = True
			print("incorrect login")

	return render(request, 'app/login.html', {"loginFailed":loginFailed})

# Register a new user
def register(request):
	# Should check for existing login and prompt for logout if found

	#context = RequestContext(request)

	registered = False
	userExists = False

	if request.method == 'POST':

		data = request.POST

		username = data['username']

		u = User.objects.filter(username=username)
		print(u)

		if u == "[]":

			password = data['password']
			email = data['email']
			address1 = data['address1']
			address2 = data['address2']
			ccn = data['ccn'].replace(" ","")
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

		else:
			userExists = True


	return render(request, 'app/register.html', {"userExists":userExists})

def deleteAccount(request):
	u = User.objects.filter(username=request.user)

	u.delete();

	response = HttpResponse()
	response.status_code = 303
	response['location'] = 'login'
	return response

def logoutUser(request):
	logout(request)
	response = HttpResponse()
	response.status_code = 303
	response['location'] = 'login'
	return response


# Purchases (All require login)
############

# Load Checkout Page
@login_required(login_url='/app/login')
def checkout(request):
	userid = request.user
	try:
		cart_invoice = Invoice.objects.filter(status='pending').get(user=userid)
	except Invoice.DoesNotExist:
		context = {'cart_items': [], 'subtotal': 0, 'tax':0, 'total':0}
		return render(request, 'app/checkout.html', context)
	
	cart_items = cart_invoice.get_item_type_counts()

	if request.method == 'POST':
		response = HttpResponse()
		response.status_code = 303
		response['location'] = 'checkout'
		if request.POST['submit'] == 'confirm order':
			#change this to the delivering state
			cart_invoice.confirm_order()
			#redirect away from the checkout page
			response['location'] = 'status'
		elif request.POST['submit'] == 'update quantities':
			#for each item update the count
			for intype, count in cart_items.iteritems():
				#The POST has a field 'product-name-quantity=###' for each type to be removed
				# construct the string to lookup and get it from the POST. If it is not present
				# in the POST then assume this type is not to be removed
				quantity_str = (intype.product_name).lower().replace(' ','-') + "-quantity"
				new_count = int(request.POST[quantity_str])
				
				if new_count > count:
					#todo Get appropriate drone
					newDrone = Drone(status='Idle', location='home')
					newDrone.save()

					#adding items of this type
					for i in range(new_count - count):
						inv_item = InvoiceItem(invoice=cart_invoice, 
									drone=newDrone, 
									inventory_type=intype)
						inv_item.save()
					intype.stock_count -= (new_count - count)
					intype.save()
					pass
				elif new_count < count:
					#removing items of this type
					cart_invoice.remove_type(intype, (count-new_count))
				else:
					#count is not changed
					pass
		elif request.POST['submit'] == 'remove selected':
			#for each item, if it is marked then remove from invoice
			invoice_types = InvoiceItem.objects.filter(invoice=cart_invoice).distinct('inventory_type')
			for intype in invoice_types:
				#The POST has a field 'product-name-marked="on"' for each type to be removed
				# construct the string to lookup and get it from the POST. If it is not present
				# in the POST then assume this type is not to be removed
				mark_str = (intype.inventory_type.product_name).lower().replace(' ','-') + "-marked"
				removal = request.POST.get(mark_str, 'off')
				if removal == 'on':
					cart_invoice.remove_type(intype.inventory_type, cart_items[intype.inventory_type])
		else:
			#unknown post
			print 'Unknown POST submit: ' + request.POST['submit']
			pass

		return response
	
	subtotal = Decimal(0.0)
	cart = []
	for itype, count in cart_items.iteritems():
		cart.append(type('',(object,),{'type': itype,'count': count, 'max':itype.stock_count + count})())
		#get the item description
		inventory_obj = InventoryType.objects.get(id=itype.id)
		#add price to subtotal
		subtotal += Decimal(count) * inventory_obj.price
	
	tax = (subtotal * Decimal(0.09)).quantize(Decimal('0.01'), rounding=ROUND_UP)
	total = subtotal + tax
	context = {'cart_items': cart, 'subtotal': subtotal, 'tax':tax, 'total':total}
	return render(request, 'app/checkout.html', context)


# Load Purchase History
@login_required(login_url='/app/login')
def history(request):
	# Use this line once users get implemented
	# invoices = Invoice.objects.filter(status='complete', user=request.user)
	invoices = Invoice.objects.filter(user=request.user, status='completed')
	context = {'invoices': invoices}
	return render(request, 'app/history.html', context)

# Load App Inventory Page (for adding to cart)
@login_required(login_url='/app/login')
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
		
		itemCount = int(request.POST['quantity'])
		#add invoice items to the invoice with the drone
		for x in range(itemCount):
			inv_item = InvoiceItem(invoice=user_invoice, inventory_type=inventoryItem)
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
@login_required(login_url='/app/login')
def status(request):
	if request.method == 'GET':
		invoices = Invoice.objects.filter(user=request.user, status='delivering')
		context = {'invoices': invoices}
		return render(request, 'app/status.html', context)
	elif request.method == 'POST':
		invoice_id = int(request.POST['invoice_id'])
		# Set invoice to completed, reload the page
		return render(request, 'app/status.html', context)

@login_required(login_url='/app/login')
def details(request, invoice=None):

	if not invoice:		
		return error404(request)		
		
	# if 'action' in request.GET:		
	# 	if request.GET['action'] == 'update':		
			
	# 		drones = Drone.objects.all().filter(invoiceitem__invoice=invoice_id).distinct()		
		
	# 		response = HttpResponse(content_type='application/json')		
	# 		response.write(dumps(sum(map(lambda drone: [drone],drones.values()),[])))		
	# 		return response		
		
	context = {		
		'invoice_id': invoice		
	}		
	return render(request, 'app/details.html', context)

# Other
########

# 404 Page
def error404(request):
	return render(request, 'app/error404.html', {'pagepath':request.path})

# CSS
def css(request):
	return render(request, request.path[1:], {},content_type='text/css')
