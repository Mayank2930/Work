import os
import json

from django.contrib import messages
from django.http import HttpResponseRedirect, FileResponse, HttpResponse
from fpdf import FPDF
from django.shortcuts import render
import pandas as pd
from zipfile import ZipFile


# This Function Creates PDF Form the two Files we input
def upload_files(request):
    if request.method == 'POST':
        count = 0
        try: 
            uploaded_files = request.FILES.getlist('paramotor_all_reports_and_final_all_reports')

            if len(uploaded_files) < 2:
                return HttpResponse("Please upload two files.")

            parm_all_reports = pd.read_excel(uploaded_files[0])
            final_report = pd.read_excel(uploaded_files[1])

            zipObj = ZipFile('MerchantReport.zip', 'w')

            paramotor_records = parm_all_reports.reset_index().to_json(orient='records')
            final_records = final_report.reset_index().to_json(orient='records')

            paramotor_data = []
            final_data = []

            paramotor_data = json.loads(paramotor_records)
            final_data = json.loads(final_records)
        except Exception as e:
            return HttpResponse(f"**Error occured: {e}**")
        
        try:
            for tran in final_data:
                if tran["TID"] != "Grand Total":
                    # Create new pdf
                    pdf = FPDF('P', 'mm', 'Letter')
                    pdf.set_auto_page_break(auto=True, margin=15)
                    pdf.add_page()

                    # Add Patramotor Logo To PDF
                    pdf.image('static/image/paramotor_logo.png', 10, 6, 30, 18)

                    # Draw a line
                    pdf.line(6, 30, 205, 30)

                    # Set Font and Font Size
                    pdf.set_font('helvetica', '', 7)

                    pdf.cell(0, 2, tran["TID"] + " Settlement Report", ln=1, align="C")

                    pdf.cell(0, 3, "Helpline Contact: 8264110077", ln=1, align="R")
                    pdf.cell(0, 2, "Email: customersupport@paramotort.com", ln=1, align="R")

                    for acount in paramotor_data:
                        if acount["TID"] == tran["TID"]:
                            pdf.cell(0, 15, "", ln=1, align="L")
                            pdf.cell(0, 4, "Legal Name: " + acount["Legal Name"], ln=1, align="L")
                            pdf.cell(0, 4, "Bank Name: " + acount["Bank name"], ln=1, align="L")
                            pdf.cell(0, 4, "Account Number: " + str(int(acount["Account Number"])), ln=1, align="L")
                            pdf.cell(0, 4, "IFSC Code: " + str(acount["bank IFSC Code"]), ln=1, align="L")
                            break

                    pdf.cell(0, 5, "", ln=1, align="L")
                    pdf.cell(10, 4, "Sr. No", border=1, align="C")
                    pdf.cell(15, 4, "Txn Date", border=1, align="C")
                    pdf.cell(15, 4, "Paid Date", border=1, align="C")
                    pdf.cell(16, 4, "TID", border=1, align="C")
                    pdf.cell(22, 4, "RRN", border=1, align="C")
                    pdf.cell(25, 4, "Card Number", border=1, align="C")
                    pdf.cell(17, 4, "Txn Amt", border=1, align="C")
                    pdf.cell(13, 4, "MSF Amt", border=1, align="C")
                    pdf.cell(10, 4, "GST", border=1, align="C")
                    pdf.cell(22, 4, "CASH@POS Amt", border=1, align="C")
                    pdf.cell(13, 4, "TDS", border=1, align="C")
                    pdf.cell(18, 4, "Net Amount", border=1, align="C")
                    pdf.cell(0, 5, "", ln=1, align="L")

                    for transaction in paramotor_data:
                        if transaction["TID"] == tran["TID"]:
                            count = count + 1
                            pdf.cell(10, 4, str(count), border=1, align="C", )
                            pdf.cell(15, 4, transaction['Txn. Date '], border=1, align="C", )
                            pdf.cell(15, 4, transaction['Payment Date'], border=1, align="C", )
                            pdf.cell(16, 4, transaction['TID'], border=1, align="C", )
                            pdf.cell(22, 4, str(int(transaction['RRN'])), border=1, align="C", )
                            pdf.cell(25, 4, str(transaction['Card Number']), border=1, align="C", )
                            pdf.cell(17, 4, str(transaction['Txn. Amt']), border=1, align="C", )
                            pdf.cell(13, 4, str(transaction['MSF.1']), border=1, align="C", )
                            pdf.cell(10, 4, str(transaction['GST']), border=1, align="C", )
                            pdf.cell(22, 4, str(transaction['CASH@POS INCENTIVE AMT']), border=1, align="C", )
                            pdf.cell(13, 4, str(transaction['TDS']), border=1, align="C", )
                            pdf.cell(18, 4, str(transaction['Net Amt']), border=1, align="C", ln=1)

                    count = 0
                    pdf.cell(10, 4, "Total", border=1, align="C", )
                    pdf.cell(15, 4, "", border=1, align="C", )
                    pdf.cell(15, 4, "", border=1, align="C", )
                    pdf.cell(16, 4, "", border=1, align="C", )
                    pdf.cell(22, 4, "", border=1, align="C", )
                    pdf.cell(25, 4, "", border=1, align="C", )
                    pdf.cell(17, 4, str(tran['Sum of Txn. Amt']), border=1, align="C", )
                    pdf.cell(13, 4, str(tran['Sum of MSF2']), border=1, align="C", )
                    pdf.cell(10, 4, str(tran['Sum of GST']), border=1, align="C", )
                    pdf.cell(22, 4, str(tran['Sum of CASH@POS INCENTIVE AMT']), border=1, align="C", )
                    pdf.cell(13, 4, str(tran['Sum of TDS']), border=1, align="C", )
                    pdf.cell(18, 4, str(tran['Sum of Net Amt']), border=1, align="C", ln=1)

                    pdf.cell(0, 5, "", ln=1, align="R")
                    pdf.cell(145, 4, " ", align="R")
                    pdf.cell(30, 4, "Gross Amount: ", border=1, align="R")
                    pdf.cell(20, 4, str(tran['Sum of Net Amt']), ln=1, border=1, align="R")
                    pdf.cell(145, 4, " ", align="R")
                    pdf.cell(30, 4, "Settlement Charges: ", border=1, align="R")
                    pdf.cell(20, 4, str(tran['Settlement Amt']), border=1, ln=1, align="R")
                    pdf.cell(145, 4, " ", align="R")
                    pdf.cell(30, 4, "Other Charges: ", border=1, align="R")
                    pdf.cell(20, 4, str(tran['Monthly Rent']), ln=1, border=1, align="R")
                    pdf.cell(145, 4, " ", align="R")
                    pdf.cell(30, 4, "Net Amount Payable: ", border=1, align="R")
                    pdf.cell(20, 4, str(tran['Net Amt']), ln=1, border=1, align="R")

                    pdf.output(tran["TID"] + '.pdf')
                    zipObj.write(tran["TID"] + '.pdf')
                else:
                    pass
        except Exception as e:
            return HttpResponse("Error occured: {e}")
        
        # Delete all pdf files
        for tran in final_data:
            if os.path.exists(tran["TID"] + '.pdf'):
                os.remove(tran["TID"] + '.pdf')

        zipObj.close()
        context = {
            'paramotor_all_reports': paramotor_data,
            'final_reports': final_data,
        }

    return render(request, 'upload_files/upload_files.html', context)


# To download the created Zip File
def download(request):
    messages.success(request, "Merchant Deleted Successful")
    try:
        file_handle = open('MerchantReport.zip', 'rb')
    except FileNotFoundError:
        messages.error(request, "File not found")
        return HttpResponseRedirect('/')
    
    return FileResponse(open('MerchantReport.zip', 'rb'), as_attachment=True)