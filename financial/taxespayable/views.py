import datetime
from django.views.generic import View, ListView, TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, JsonResponse, Http404, HttpResponse
from mrstype.models import Mrstype
from financial.utils import Render
from django.utils import timezone
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from companyparameter.models import Companyparameter
from accountspayable.models import Apmain
from checkvoucher.models import Cvmain
from journalvoucher.models import Jvmain
from officialreceipt.models import Ormain
from subledger.models import Subledger
from customer.models import Customer
from chartofaccount.models import Chartofaccount
from collections import namedtuple
from django.db import connection
from django.template.loader import render_to_string
import pandas as pd
import io
import xlsxwriter
import datetime
from datetime import timedelta


class IndexView(TemplateView):
    template_name = 'taxespayable/index.html'

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        context['chart'] = Chartofaccount.objects.filter(isdeleted=0, accounttype='P',id__in=[315,316,318]).order_by('accountcode')

        return context

#@csrf_exempt
def transgenerate(request):
    dto = request.GET["dto"]
    dfrom = request.GET["dfrom"]
    transaction = request.GET["transaction"]
    chartofaccount = request.GET["chartofaccount"]
    payeecode = request.GET["payeecode"]
    payeename = request.GET["payeename"]
    report = request.GET["report"]

    viewhtml = ''
    context = {}

    if report == '1':
        print "transaction listing"

        datalist = queryTransaction(dto, dfrom, transaction, chartofaccount, payeecode, payeename)
        #print datalist

        context['data'] = datalist
        viewhtml = render_to_string('taxespayable/transaction_listing.html', context)
    elif report == '2':
        print "schedule"

        datalist = querySchedule(dto, dfrom, transaction, chartofaccount, payeecode, payeename)
        #print datalist

        context['data'] = datalist
        viewhtml = render_to_string('taxespayable/schedule.html', context)

    elif report == '3':
        print "alphalist summary"
        datalist = queryAlphalist(1, dto, dfrom, transaction, chartofaccount, payeecode, payeename)

        ttaxesable = 0
        ttax = 0

        for data in datalist:
            ttaxesable += data.taxesable
            ttax += data.tax

        context['datalist'] = datalist
        context['beg'] = []
        context['dfrom'] = datetime.datetime.strptime(dfrom, '%Y-%m-%d')
        context['dto'] = datetime.datetime.strptime(dto, '%Y-%m-%d')
        context['ttaxesable'] = ttaxesable
        context['ttax'] = ttax
        viewhtml = render_to_string('taxespayable/transaction_alphalist_summary.html', context)
    elif report == '4':
        print "alphalist detail"
        datalist = queryAlphalist(2, dto, dfrom, transaction, chartofaccount, payeecode, payeename)

        ttaxesable = 0
        ttax = 0

        for data in datalist:
            ttaxesable += data.taxesable
            ttax += data.tax

        context['datalist'] = datalist
        context['beg'] = []
        context['dfrom'] = datetime.datetime.strptime(dfrom, '%Y-%m-%d')
        context['dto'] = datetime.datetime.strptime(dto, '%Y-%m-%d')
        context['ttaxesable'] = ttaxesable
        context['ttax'] = ttax
        viewhtml = render_to_string('taxespayable/transaction_alphalist_detail.html', context)

    data = {
        'status': 'success',
        'viewhtml': viewhtml,

    }
    return JsonResponse(data)

@method_decorator(login_required, name='dispatch')
class TransExcel(View):
    def get(self, request):

        dto = request.GET["dto"]
        dfrom = request.GET["dfrom"]
        transaction = request.GET["transaction"]
        chartofaccount = request.GET["chartofaccount"]
        payeecode = request.GET["payeecode"]
        payeename = request.GET["payeename"]
        report = request.GET["report"]

        filename = 'taxespayable.xls'


        output = io.BytesIO()

        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        # variables
        bold = workbook.add_format({'bold': 1})
        formatdate = workbook.add_format({'num_format': 'MM-DD/YYYY'})
        centertext = workbook.add_format({'bold': 1, 'align': 'center'})

        if report == '1':
            print "transaction listing"
            filename = "tranasction_listing.xlsx"
            datalist = queryTransaction(dto, dfrom, transaction, chartofaccount, payeecode, payeename)

            worksheet.write('A1', 'Doc Date')
            worksheet.write('B1', 'Doc Type')
            worksheet.write('C1', 'Doc Num')
            worksheet.write('D1', 'Particulars')
            worksheet.write('E1', 'Code')
            worksheet.write('F1', 'Supplier')
            worksheet.write('G1', 'Last Name')
            worksheet.write('H1', 'First Name')
            worksheet.write('I1', 'Middle Name')
            worksheet.write('J1', 'Debit')
            worksheet.write('K1', 'Credit')
            worksheet.write('L1', 'Rate')
            worksheet.write('M1', 'Tax')
            worksheet.write('N1', 'Gross')
            worksheet.write('O1', 'Address')
            worksheet.write('P1', 'TIN')

            row = 1
            col = 0
            ttaxesable = 0
            ttax = 0
            #
            counter = 1
            for data in datalist:
                worksheet.write(row, col, data.document_date, formatdate)
                worksheet.write(row, col + 1, data.document_type)
                worksheet.write(row, col + 2, data.document_num)
                worksheet.write(row, col + 3, data.particulars)
                worksheet.write(row, col + 4, data.suppliercode)
                worksheet.write(row, col + 5, data.supplier)
                worksheet.write(row, col + 6, data.lname)
                worksheet.write(row, col + 7, data.fname)
                worksheet.write(row, col + 8, data.mname)
                worksheet.write(row, col + 9, data.debit)
                worksheet.write(row, col + 10, data.credit)
                worksheet.write(row, col + 11, data.atcrate)
                worksheet.write(row, col + 12, data.tax)
                worksheet.write(row, col + 13, data.taxesable)
                worksheet.write(row, col + 14, data.address)
                worksheet.write(row, col + 15   , data.tin)

                row += 1

        elif report == '2':
            print "schedule"
            filename = "schedule.xlsx"
            datalist = querySchedule(dto, dfrom, transaction, chartofaccount, payeecode, payeename)

            worksheet.write('A1', 'Code')
            worksheet.write('B1', 'Supplier')
            worksheet.write('C1', 'Last Name')
            worksheet.write('D1', 'First Name')
            worksheet.write('E1', 'Middle Name')
            worksheet.write('F1', 'Rate')
            worksheet.write('G1', 'Tax')
            worksheet.write('H1', 'Gross')
            worksheet.write('I1', 'Address')
            worksheet.write('J1', 'TIN')

            row = 1
            col = 0
            ttaxesable = 0
            ttax = 0
            #
            counter = 1
            for data in datalist:
                worksheet.write(row, col, data.suppliercode)
                worksheet.write(row, col + 1, data.supplier)
                worksheet.write(row, col + 2, data.lname)
                worksheet.write(row, col + 3, data.fname)
                worksheet.write(row, col + 4, data.mname)
                worksheet.write(row, col + 5, data.atcrate)
                worksheet.write(row, col + 6, data.tax)
                worksheet.write(row, col + 7, data.taxesable)
                worksheet.write(row, col + 8, data.address)
                worksheet.write(row, col + 9, data.tin)

                row += 1

        elif report == '3':
            print "alphalist summary"
            filename = "alphalist_summary.xlsx"
            ddfrom = datetime.datetime.strptime(dfrom, '%Y-%m-%d')

            print ddfrom

            datalist = queryAlphalist(1, dto, dfrom, transaction, chartofaccount, payeecode, payeename)

            # title
            worksheet.write('A1', 'HQAP')
            worksheet.write('B1', 'H1601EQ')
            worksheet.write('C1', '000803607')
            worksheet.write('D1', '0000')
            worksheet.write('E1', 'THE PHILIPPINE DAILY INQUIRER INC')
            worksheet.write('F1', '16/09/2022')
            worksheet.write('G1', '116')

            row = 1
            col = 0
            ttaxesable = 0
            ttax = 0
            #
            counter = 1
            for data in datalist:
                worksheet.write(row, col, 'D1')
                worksheet.write(row, col + 1, '1601EQ')
                worksheet.write(row, col + 2, counter)
                worksheet.write(row, col + 3, data.tina)
                worksheet.write(row, col + 4, data.tinb)
                if data.suppliertype_id == 3:
                    worksheet.write(row, col + 5, data.supplier)
                else:
                    worksheet.write(row, col + 6, data.lname)
                    worksheet.write(row, col + 7, data.mname)
                    worksheet.write(row, col + 8, data.fname)

                worksheet.write(row, col + 9, float(format(data.taxesable, '.2f')))
                worksheet.write(row, col + 10, float(format(data.tax, '.2f')))

                row += 1
                counter += 1
                ttaxesable += data.taxesable
                ttax += data.tax
            #
            worksheet.write(row, col, 'C1')
            worksheet.write(row, col + 1, '1601EQ')
            worksheet.write(row, col + 2, '000803607')
            worksheet.write(row, col + 3, '')
            worksheet.write(row, col + 4, '16/09/2022')
            worksheet.write(row, col + 5, float(format(ttaxesable, '.2f')))
            worksheet.write(row, col + 6, float(format(ttax, '.2f')))

        elif report == '4':
            print "alphalist detail"
            filename = "alphalist_detail.xlsx"

            datalist = queryAlphalist(2, dto, dfrom, transaction, chartofaccount, payeecode, payeename)

            # title
            worksheet.write('A1', 'HQAP')
            worksheet.write('B1', 'H1601EQ')
            worksheet.write('C1', '000803607')
            worksheet.write('D1', '0000')
            worksheet.write('E1', 'THE PHILIPPINE DAILY INQUIRER INC')
            worksheet.write('F1', '16/09/2022')
            worksheet.write('G1', '116')

            row = 1
            col = 0
            ttaxesable = 0
            ttax = 0
            #
            counter = 1
            for data in datalist:
                worksheet.write(row, col, 'D1')
                worksheet.write(row, col + 1, '1601EQ')
                worksheet.write(row, col + 2, counter)
                worksheet.write(row, col + 3, data.tina)
                worksheet.write(row, col + 4, data.tinb)
                if data.suppliertype_id == 3:
                    worksheet.write(row, col + 5, data.supplier)
                else:
                    worksheet.write(row, col + 6, data.lname)
                    worksheet.write(row, col + 7, data.mname)
                    worksheet.write(row, col + 8, data.fname)

                worksheet.write(row, col + 9, float(format(data.taxesable, '.2f')))
                worksheet.write(row, col + 10, float(format(data.tax, '.2f')))

                row += 1
                counter += 1
                ttaxesable += data.taxesable
                ttax += data.tax
            #
            worksheet.write(row, col, 'C1')
            worksheet.write(row, col + 1, '1601EQ')
            worksheet.write(row, col + 2, '000803607')
            worksheet.write(row, col + 3, '')
            worksheet.write(row, col + 4, '16/09/2022')
            worksheet.write(row, col + 5, float(format(ttaxesable, '.2f')))
            worksheet.write(row, col + 6, float(format(ttax, '.2f')))


        workbook.close()

        # Rewind the buffer.

        output.seek(0)

        print filename

        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response



def queryAlphalist(type, dto, dfrom, transaction, chartofaccount, payeecode, payeename):
    print type
    conchart = "AND s.chartofaccount_id IN (315,316,318)"
    orderby = ""
    groupby = ""
    conpayeecode = ""
    conpayeename = ""

    if type == 1:
        groupby = "GROUP BY YEAR(s.document_date), s.atccode, s.document_supplier_id "
    else:
        groupby = "GROUP BY YEAR(s.document_date), s.atccode, s.document_supplier_id, s.id "

    if chartofaccount:
        conchart = "AND s.chartofaccount_id IN ("+chartofaccount+")"

    if payeename:
        conpayeename = "WHERE z.suppliername LIKE '%"+str(payeename)+"%'"

    print conchart
    ''' Create query '''
    cursor = connection.cursor()


    query = "SELECT z.* " \
            "FROM ( " \
            "SELECT s.id, s.document_supplier_id, sup.suppliertype_id, s.document_type, s.document_num, s.document_date, sup.tin, SUBSTRING_INDEX(sup.tin, '-', 3) AS tina, LPAD(SUBSTRING_INDEX(sup.tin, '-', -1), 4 , '0') AS tinb, " \
            "IF(sup.suppliertype_id = 4, '', sup.name) AS supplier, sup.name AS suppliername, " \
            "s.atccode, IFNULL((s.atcrate / 100), 0) AS atcrate, s.balancecode, s.amount, " \
            "IF(IFNULL(s.atcrate, 0) = 0, SUM(s.amount), SUM(s.amount / (s.atcrate/100))) AS taxesable, SUM(s.amount) AS tax, " \
            "IF(sup.suppliertype_id = 4, IF(emp.id != '', emp.firstname, SUBSTRING_INDEX(REPLACE(sup.name,'*',''), ' ', 1)), '') AS fname, " \
            "IF(sup.suppliertype_id = 4, IF(emp.id != '', emp.middlename, ''), '') AS mname, " \
            "IF(sup.suppliertype_id = 4, IF(emp.id != '', emp.lastname, SUBSTRING_INDEX(REPLACE(sup.name,'*',''), ' ', -1)), '') AS lname, " \
            "emp.id AS emp " \
            "FROM subledger AS s " \
            "LEFT OUTER JOIN supplier AS sup ON sup.id = s.document_supplier_id " \
            "LEFT OUTER JOIN employee AS emp ON emp.supplier_id = sup.id " \
            "WHERE DATE(s.document_date) >= '"+str(dfrom)+"' AND DATE(s.document_date) <= '"+str(dto)+"' " \
            +""+str(conchart)+" "+str(groupby)+ "ORDER BY sup.suppliertype_id ASC, sup.name ASC " \
            ") AS z " \
            +""+str(conpayeename)+" "+"ORDER BY z.suppliertype_id ASC, z.supplier ASC, z.lname, z.document_date ASC"

    print query

    cursor.execute(query)
    result = namedtuplefetchall(cursor)

    return result

def queryTransaction(dto, dfrom, transaction, chartofaccount, payeecode, payeename):
    print type
    conchart = "AND s.chartofaccount_id IN (315,316,318)"
    orderby = ""
    groupby = ""
    conpayeecode = ""
    conpayeename = ""

    if chartofaccount:
        conchart = "AND s.chartofaccount_id IN ("+chartofaccount+")"

    if payeename:
        conpayeename = "AND  sup.name LIKE '%"+str(payeename)+"%'"

    print conchart
    ''' Create query '''
    cursor = connection.cursor()


    query = "SELECT s.id, s.document_supplier_id, sup.suppliertype_id, s.document_type, s.document_num, s.document_date, sup.tin, " \
            "SUBSTRING_INDEX(sup.tin, '-', 3) AS tina, LPAD(SUBSTRING_INDEX(sup.tin, '-', -1), 4 , '0') AS tinb, " \
            "s.particulars, sup.code AS suppliercode, sup.name AS supplier, " \
            "s.atccode, IFNULL((s.atcrate / 100) * 100, 0) AS atcrate, s.balancecode, s.amount, " \
            "IF(IFNULL(s.atcrate, 0) = 0, (s.amount), (s.amount / (s.atcrate/100))) AS taxesable, (s.amount) AS tax, " \
            "IF(s.balancecode = 'D', s.amount, 0) AS debit, IF(s.balancecode = 'C', s.amount, 0) AS credit, " \
            "IF(sup.suppliertype_id = 4, IF(emp.id != '', emp.firstname, SUBSTRING_INDEX(REPLACE(sup.name,'*',''), ' ', 1)), '') AS fname, " \
            "IF(sup.suppliertype_id = 4, IF(emp.id != '', emp.middlename, ''), '') AS mname, " \
            "IF(sup.suppliertype_id = 4, IF(emp.id != '', emp.lastname, SUBSTRING_INDEX(REPLACE(sup.name,'*',''), ' ', -1)), '') AS lname, " \
            "emp.id AS emp, CONCAT(sup.address1, ' ', sup.address2, ' ', sup.address3) AS address " \
            "FROM subledger AS s " \
            "LEFT OUTER JOIN supplier AS sup ON sup.id = s.document_supplier_id " \
            "LEFT OUTER JOIN employee AS emp ON emp.supplier_id = sup.id " \
            "WHERE DATE(s.document_date) >= '"+str(dfrom)+"' AND DATE(s.document_date) <= '"+str(dto)+"' " \
            +""+str(conchart)+" "+ " " \
            +""+str(conpayeename)+" "+"ORDER BY s.document_date,  FIELD(s.document_type, 'AP', 'CV', 'JV', 'OR'), s.document_num, sup.name ASC"

    print query

    cursor.execute(query)
    result = namedtuplefetchall(cursor)

    return result

def querySchedule(dto, dfrom, transaction, chartofaccount, payeecode, payeename):
    print type
    conchart = "AND s.chartofaccount_id IN (315,316,318)"
    orderby = ""
    groupby = ""
    conpayeecode = ""
    conpayeename = ""

    if chartofaccount:
        conchart = "AND s.chartofaccount_id IN ("+chartofaccount+")"

    if payeename:
        conpayeename = "AND  sup.name LIKE '%"+str(payeename)+"%'"

    print conchart
    ''' Create query '''
    cursor = connection.cursor()


    query = "SELECT s.id, s.document_supplier_id, sup.suppliertype_id, s.document_type, s.document_num, s.document_date, sup.tin, " \
            "SUBSTRING_INDEX(sup.tin, '-', 3) AS tina, LPAD(SUBSTRING_INDEX(sup.tin, '-', -1), 4 , '0') AS tinb, " \
            "s.particulars, sup.code AS suppliercode, sup.name AS supplier, " \
            "s.atccode, IFNULL((s.atcrate / 100) * 100, 0) AS atcrate, s.balancecode, SUM(s.amount) AS amount, " \
            "IF(IFNULL(s.atcrate, 0) = 0, SUM(s.amount), SUM(s.amount / (s.atcrate/100))) AS taxesable, SUM(s.amount) AS tax, " \
            "IF(s.balancecode = 'D', SUM(s.amount), 0) AS debit, IF(s.balancecode = 'C', SUM(s.amount), 0) AS credit," \
            "IF(sup.suppliertype_id = 4, IF(emp.id != '', emp.firstname, SUBSTRING_INDEX(REPLACE(sup.name,'*',''), ' ', 1)), '') AS fname, " \
            "IF(sup.suppliertype_id = 4, IF(emp.id != '', emp.middlename, ''), '') AS mname, " \
            "IF(sup.suppliertype_id = 4, IF(emp.id != '', emp.lastname, SUBSTRING_INDEX(REPLACE(sup.name,'*',''), ' ', -1)), '') AS lname, " \
            "emp.id AS emp, CONCAT(sup.address1, ' ', sup.address2, ' ', sup.address3) AS address " \
            "FROM subledger AS s " \
            "LEFT OUTER JOIN supplier AS sup ON sup.id = s.document_supplier_id " \
            "LEFT OUTER JOIN employee AS emp ON emp.supplier_id = sup.id " \
            "WHERE DATE(s.document_date) >= '"+str(dfrom)+"' AND DATE(s.document_date) <= '"+str(dto)+"' " \
            +""+str(conchart)+" "+ " " \
            +""+str(conpayeename)+" "+"GROUP BY sup.code, atcrate ORDER BY sup.name ASC"

    print query

    cursor.execute(query)
    result = namedtuplefetchall(cursor)

    return result

def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]