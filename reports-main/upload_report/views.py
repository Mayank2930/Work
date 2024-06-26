import os
import json

from django.contrib import messages
from django.http import HttpResponseRedirect, FileResponse, HttpResponse
from fpdf import FPDF
from django.shortcuts import render, redirect
import pandas as pd
from zipfile import ZipFile

# This Function Creates PDF Form the two Files we input
import os
import json
from zipfile import ZipFile
from django.shortcuts import render, HttpResponse
from fpdf import FPDF
import pandas as pd

import pandas as pd

def file_type(request, file1, file2):
    if file1.name.endswith('.xlsx'):
        paramotor_data = pd.read_excel(file1)
    elif file1.name.endswith('.csv'):
        paramotor_data = pd.read_csv(file1)
    else:
        messages.error(request, "Unsupported file format for file1. Only .xlsx and .csv files are supported.")
        return redirect('/')

    if file2.name.endswith('.xlsx'):
        final_data = pd.read_excel(file2)
    elif file2.name.endswith('.csv'):
        final_data = pd.read_csv(file2)
    else:
        messages.error(request, "Unsupported file format for file1. Only .xlsx and .csv files are supported.")
        return redirect('/')
    
    return paramotor_data, final_data

def validate_file(request, file1, file2):
    COLS_IN_FILE1 = [ 'Sr.No', 'MID', 'TID', 'Merchant Name', 'DBA Name', 'City',
       'Card Number', 'Auth Code', 'Txn. Date ', 'Settled Date',
       'Batch Number', 'Payment Date', 'Txn. Amt', 'MSF', '    MSF GST',
       '         TPC', '     TPC GST', '   TOTAL GST', '        IGST',
       '        CGST', '   SGST/UGST', 'Cash Pos Incent', '        Net Amount',
       'PAYMENT_CURRENCY', 'Txn Cur', '        Adj. Amt.', ' Adj. Code',
       'Adj code Discription', 'Adj Narration                 ',
       'Sale/refund         ', 'RRN', 'Local/Intl. ', 'Ori.Txn.Amt    ',
       'MCC  ', ' MSF EXEMPT AMT', 'ENTRY_MODE  ', 'CARD TYPE ', 'AGEING ',
       'SCHEME    ', 'CHANNEL', 'SUB CUSTOMER        ', 'File Role',
       'MSF PARAMOTOR', 'MSF.1', 'GST', 'GST+MSF', 'CASH@POS INCENTIVE AMT',
       'TDS', 'Net Amt', 'Legal Name', 'Account Number', 'Bank name',
       'bank IFSC Code', 'Pan Number']


    COLS_IN_FILE2 = [
        'TID', 
        'Merchant Name',
        'SUB CUSTOMER', 
        'CHANNEL',
        'Count of Txn. Amt',
        'Sum of Txn. Amt', 
        'Sum of MSF', 
        'Sum of MSF GST',
        'Sum of Cash Pos Incent',
        'Sum of Net Amount', 
        'Sum of MSF2', 
        'Sum of GST', 
        'Sum of CASH@POS INCENTIVE AMT',
        'Sum of TDS', 
        'Sum of Net Amt', 
        'Hold Payment', 
        'Monthly Rent', 
        'Vas Charges',
        'Settlement Amt',
        'Net Amt']

    x, y = file_type(request, file1, file2)

    file1_validate = all(col in x.columns for col in COLS_IN_FILE1)
    file2_validate = all(col in y.columns for col in COLS_IN_FILE2)

    if file1_validate and file2_validate:
        return x, y
    else:
        missing_cols_file1 = [col for col in COLS_IN_FILE1 if col not in x.columns]
        missing_cols_file2 = [col for col in COLS_IN_FILE2 if col not in y.columns]
        
        error_message = "Validation failed. "
        if missing_cols_file1:
            error_message += f"Missing columns in file 1: {', '.join(missing_cols_file1)}. "
        if missing_cols_file2:
            error_message += f"Missing columns in file 2: {', '.join(missing_cols_file2)}. "
        
        messages.error(request, error_message)
        return redirect('/')

def upload_files(request):
    if request.method == 'POST':
        try:
            paramotor_data = None
            final_data = None
            
            count = 0
            FILE_1 = request.FILES['paramotor_all_reports']
            FILE_2 = request.FILES['final_all_reports']

            paramotor_data, final_data = validate_file(request, FILE_1, FILE_2)

            if paramotor_data is not None and final_data is not None:
                ZIP_OBJ = ZipFile('MerchantReport.zip', 'w')
                
                paramotor_records = paramotor_data.reset_index().to_json(orient='records')
                final_records = final_data.reset_index().to_json(orient='records')

                paramotor_data = json.loads(paramotor_records)
                final_data = json.loads(final_records)

                for tran in final_data:
                    if tran["TID"] != "Grand Total":
                        pdf = FPDF('P', 'mm', 'Letter')
                        pdf.set_auto_page_break(auto=True, margin=15)
                        pdf.add_page()

                        pdf.image('static/image/paramotor_logo.png', 10, 6, 30, 18)

                        pdf.line(6, 30, 205, 30)

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
                                pdf.cell(10, 4, str(count), border=1, align="C")
                                pdf.cell(15, 4, transaction['Txn. Date '], border=1, align="C")
                                pdf.cell(15, 4, transaction['Payment Date'], border=1, align="C")
                                pdf.cell(16, 4, transaction['TID'], border=1, align="C")
                                pdf.cell(22, 4, str(int(transaction['RRN'])), border=1, align="C")
                                pdf.cell(25, 4, str(transaction['Card Number']), border=1, align="C")
                                pdf.cell(17, 4, str(transaction['Txn. Amt']), border=1, align="C")
                                pdf.cell(13, 4, str(transaction['MSF.1']), border=1, align="C")
                                pdf.cell(10, 4, str(transaction['GST']), border=1, align="C")
                                pdf.cell(22, 4, str(transaction['CASH@POS INCENTIVE AMT']), border=1, align="C")
                                pdf.cell(13, 4, str(transaction['TDS']), border=1, align="C")
                                pdf.cell(18, 4, str(transaction['Net Amt']), border=1, align="C", ln=1)

                        count = 0
                        pdf.cell(10, 4, "Total", border=1, align="C")
                        pdf.cell(15, 4, "", border=1, align="C")
                        pdf.cell(15, 4, "", border=1, align="C")
                        pdf.cell(16, 4, "", border=1, align="C")
                        pdf.cell(22, 4, "", border=1, align="C")
                        pdf.cell(25, 4, "", border=1, align="C")
                        pdf.cell(17, 4, str(tran['Sum of Txn. Amt']), border=1, align="C")
                        pdf.cell(13, 4, str(tran['Sum of MSF2']), border=1, align="C")
                        pdf.cell(10, 4, str(tran['Sum of GST']), border=1, align="C")
                        pdf.cell(22, 4, str(tran['Sum of CASH@POS INCENTIVE AMT']), border=1, align="C")
                        pdf.cell(13, 4, str(tran['Sum of TDS']), border=1, align="C")
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
                        ZIP_OBJ.write(tran["TID"] + '.pdf')

                ZIP_OBJ.close()
                
                # Delete all pdf files after creating the zip
                for tran in final_data:
                    pdf_file = tran["TID"] + '.pdf'
                    if os.path.exists(pdf_file):
                        os.remove(pdf_file)

                context = {
                    'paramotor_all_reports': paramotor_data,
                    'final_reports': final_data,
                }

                return render(request, 'upload_files/upload_files.html', context)
        
            else:
                messages.error(request, "***One or both files could not be uploaded or are in unsupported format.***")
                return redirect('/')
        
        except Exception as e:
            messages.error(request, f"Error occurred: {e}")
            return redirect('/')
    else:
        messages.error(request, "Method not supported")
        return redirect('/')

# To download the created Zip File
def download(request):
    try:
        return FileResponse(open('MerchantReport.zip', 'rb'), as_attachment=True)
    except FileNotFoundError:
        messages.error(request, "File not found")
        return HttpResponseRedirect('/')
    
    