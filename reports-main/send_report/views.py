from __future__ import print_function

import time
import os
from .models import EmailLog
from zipfile import ZipFile
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from openpyxl.packaging.manifest import mimetypes
from django.http import HttpResponse

from merchant.models import Merchant

from django.core.mail import EmailMessage
from django.conf import settings

from django.contrib import messages

@login_required
def check_merchant(request):
     if request.method == "POST":
        try:
            # First i am deleting every .ZIP file from the Directory
            txt_files = [f for f in os.listdir('.') if f.endswith('.zip')]
            for uploaded_file in txt_files:
                if os.path.exists(uploaded_file) == "MerchantReport.zip":
                    pass
                else:
                    if os.path.exists(uploaded_file):
                        os.remove(uploaded_file)

            # Selecting the ZIP File from Template
            zipfile = request.FILES.get('send_report')

            # to save the Temporary file in memory in the local disk
            zipfile_name = str(zipfile)
            print(f'[INFO] File Name: {zipfile_name}')

            with open(zipfile_name, 'wb+') as f:
                for chunk in zipfile.chunks():
                    f.write(chunk)

            # Opening File With python ZipFile package
            with ZipFile(zipfile, 'r') as zip:

                zip_file = zip.namelist()

                # Creating Empty list to append for loop values to it
                existing_tids = []
                non_existing_tids = []

                for file in zip_file:
                    file_name = file.replace(".pdf", "")
                    zip.extract(file)

                    merchant = Merchant.objects.filter(tid=file_name).exists()

                    if merchant:
                        existing_tid = file_name
                        existing_tids.append(existing_tid)

                    else:
                        non_existing_tid = file_name
                        non_existing_tids.append(non_existing_tid)

                    if os.path.exists(file):
                        os.remove(file)
            context = {
                "existing_tids": existing_tids,
                "non_existing_tids": non_existing_tids,

            }
        except FileNotFoundError:
            messages.error(request, "File not found")
            return redirect('/')
        except Exception as e:
            messages.error(request, f"Error occured: {e}")
            return redirect('/')

        return render(request, "sent_mail/check_merchant.html", context)

def send_reports_and_log_mail(request):
    if request.method == 'POST':
        try:
            payment_date = request.POST.get('paid_date')
            recipient_list = []
            rejected_mail_users = []
            unsent_mail_users = []
            sent_mail_count = 0
            unsent_mail_count = 0
            rejected_mail_count = 0
            txt_files = [f for f in os.listdir('.') if f.endswith('.zip')]
            for uploaded_file in txt_files:

                    with ZipFile(uploaded_file, 'r') as zip:

                        zip_file = zip.namelist()
                        print(zip_file)
                        for file in zip_file:
                            file_name = file.replace(".pdf", "")
                            zip.extract(file)

                            merchant = Merchant.objects.filter(tid=file_name)

                            if merchant.exists():
                            
                                for user in merchant:
                                    if user.secondary_email == 'nan':
                                        cc = None
                                    else:
                                        cc = user.secondary_email
                                    if user.bcc_email == 'nan':
                                        bcc = None
                                    else:
                                        bcc = user.bcc_email
                                    if user.primary_email != "nan":
                                        print(file)
                                        email = EmailMessage(
                                            user.file_name + "-" + payment_date,
                                            "Body goes here",
                                            None,
                                            to = [user.primary_email],
                                            cc = [user.secondary_email],
                                            bcc = [user.bcc_email],
                                            headers={"Message-ID": "foo"},
                                        )
                                        email.attach_file(file)
                                        try:
                                            sent_mail = email.send(fail_silently=False)
                                            sent_main_user = user
                                            recipient_list.append(sent_main_user)
                                            sent_mail_count += 1
                                            # Logging the sent mail
                                            EmailLog.objects.create(recipient=user.primary_email)
                                        except Exception as e:
                                            print(f"Error sending email to {user.primary_email}: {e}")
                                            rejected_mail_count += 1
                                            rejected_mail_users.append(user)
                                    else:
                                        rejected_mail_count += 1
                                        rejected_mail_users.append(user)
                            else:
                                unsent_mail_count += 1
                                unsent_mail_users.append(file_name)
                            #time.sleep(12)

                            if os.path.exists(file):
                                os.remove(file)
        except Exception as e:
            messages.error(request, "Error occured: {e}.")
            return redirect('/')
                      
        context = {
            "sent_mail_count": sent_mail_count,
            "rejected_mail_count": rejected_mail_count,
            "rejected_mail_users":rejected_mail_users,
            "sent_mail_users": recipient_list,
            "unsent_mail_count": unsent_mail_count,
            "unsent_mail_users": unsent_mail_users,
        }

    return render(request, "sent_mail/send_mail.html", context)