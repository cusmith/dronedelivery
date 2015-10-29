from django.http import HttpResponse
from django.shortcuts import render

from app.models import InvoiceItem, Invoice, InventoryType


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

def inventory(request):
	if request.method == 'POST':
		
		#update the inventory count
		inventoryItem = InventoryType.objects.get(product_name=request.POST['item'])
		inventoryItem.stock_count = inventoryItem.stock_count - int(request.POST['quantity'])
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
