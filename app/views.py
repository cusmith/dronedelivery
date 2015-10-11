from django.http import HttpResponse
from django.shortcuts import render

from app.models import InvoiceItem, Invoice


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

def css(request):
	return render(request, request.path[1:], {},content_type='text/css')

def error404(request):
	return render(request, 'app/error404.html', {'pagepath':request.path})