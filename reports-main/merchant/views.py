from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import MerchantForm
from django.contrib import messages
import pandas as pd
import os
# Create your views here.
from .models import Merchant
import logger


# Home Screen
@login_required
def home(request):
    try:
        user = request.user
        merchant = Merchant.objects.all()
        context = {
            "user": user,
            "merchant": merchant,
        }
        return render(request, 'merchant/home.html', context)
    except Merchant.DoesNotExist: 
        context = {
            "user": user,
            "merchant": None,
            "Error" : "Does not found"
        }
        return render(request, 'merchant/home.html', context)
    except Exception as e:
        return HttpResponse(f"Error occured : {e}")


# A form to create Merchant
@login_required
def merchant_form(request):
    user = request.user
    try:
        if request.method == 'POST':
            form = MerchantForm(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/')
        else:
            form = MerchantForm(initial={'key': 'value'})

        context = {
            "user": user,
            "form": form,
        }
        return render(request, 'merchant/merchant_form.html', context)
    except Exception as e:
        return HttpResponse(f"Error : {e}")

# This Function lets to bulk upload new merchant
@login_required
def merchant_bulk_upload(request):
    if request.method == 'POST':
        try: 
            # bulk = (r'C:\Users\hp\OneDrive\Desktop\Merchantdataformat.xlsx')

            bulk_merch = pd.read_excel(request.FILES.get('bulk_merchant'))

            bulk_merchant = bulk_merch.values.tolist()

            for merchant in bulk_merchant:
                if Merchant.objects.filter(tid=merchant[1]).exists():
                    print("merchant already exists")
                else:
                    file_name = merchant[0]
                    tid = merchant[1]
                    aggregator_module = merchant[2]
                    legal_name = merchant[3]
                    primary_email = merchant[4]
                    secondary_email = merchant[5]
                    bcc_email = merchant[6]

                    save_merchant = Merchant(
                        file_name=file_name,
                        tid=tid,
                        aggregator_module=aggregator_module,
                        legal_name=legal_name,
                        primary_email=primary_email,
                        secondary_email=secondary_email,
                        bcc_email=bcc_email
                    )
                    save_merchant.save()
            return HttpResponseRedirect("/")
        except Exception as e:
            return HttpResponse(f"Error occured: {e}")
    else:
        pass
        return render(request, 'merchant/merchant_form.html')


@login_required
def merchant_detail(request, id):
        merchant = get_object_or_404(Merchant, id=id)

        try: 
            form = MerchantForm(request.POST or None, instance=merchant)

            # add form dictionary to context
            context = {
                'merchant': merchant,
                'form': form,
            }

            if request.method == 'POST':
                    if form.is_valid():
                        form.save()
                        messages.success(request, "Merchant Updated")
                    else:
                        messages.error(request, "Form is not valid")

            return render(request, "merchant/merchant_detail.html", context)
        except Exception as e:
            return HttpResponse(f"Error occured: {e}")

@login_required
def delete_merchant(request, id):
        merchant = get_object_or_404(Merchant, id=id)
        print(merchant)
        merchant.delete()
        return HttpResponseRedirect("/")




