from django.http import HttpResponse
from django.shortcuts import render

from app.models import InvoiceItem, Invoice


def index(request):
	pending_invoice_items = InvoiceItem.objects.filter(invoice__status='pending')
	context = {'pending_invoice_items': pending_invoice_items}
	return render(request, 'app/index.html', context)
