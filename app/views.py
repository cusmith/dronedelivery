from django.http import HttpResponse
from django.shortcuts import render

from app.models import User, InvoiceItem, Invoice, Drone, InventoryType


def index(request):
	pending_invoice_items = InvoiceItem.objects.filter(invoice__status='pending')
	context = {'pending_invoice_items': pending_invoice_items}
	return render(request, 'app/index.html', context)

def login(request):
	# Should check for existing login and redirect to account page if found

	if request.method == 'POST':
		response = HttpResponse()
		response.status_code = 303
		response['location'] = 'account'
		return response

	return render(request, 'app/login.html', {})

def register(request):
	# Should check for existing login and prompt for logout if found

	if request.method == 'POST':
		response = HttpResponse()
		response.status_code = 303
		response['location'] = 'account'
		return response

	return render(request, 'app/register.html', {})

def account(request):
	return render(request, 'app/account.html', {})

def checkout(request):
	return render(request, 'app/checkout.html', {})

def inventory(request):
	if request.method == 'POST':
		#todo get the user info
		username = 'uname'
		
		#get the invoice
		try:
			user_invoice = Invoice.objects.filter(status='pending').get(user__username=username)
		except Invoice.DoesNotExist:
			user_invoice = Invoice(status='pending', user=User.objects.get(username=username))
			user_invoice.save()

		inventoryItem = InventoryType.objects.get(product_name=request.POST['item'])
		
		#todo get appropriate drone
		newDrone = Drone(status='Idle', location='home')
		newDrone.save()
		
		itemCount = int(request.POST['quantity'])
		#add invoice items to the invoice with the drone
		for x in range(itemCount):
			print x
			inv_item = InvoiceItem(invoice=user_invoice, drone=newDrone, inventory_type=inventoryItem)
			inv_item.save()
		
		#update the inventory count
		inventoryItem.stock_count = inventoryItem.stock_count - itemCount
		inventoryItem.save()
		
		response = HttpResponse()
		response.status_code = 303
		response['location'] = 'inventory'
		return response
	
	inventory_items = InventoryType.objects.all()
	context = {'inventory_items': inventory_items}
	return render(request, 'app/inventory.html', context)

def css(request):
	return render(request, request.path[1:], {},content_type='text/css')

def error404(request):
	return render(request, 'app/error404.html', {'pagepath':request.path})
