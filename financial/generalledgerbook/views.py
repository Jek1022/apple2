from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from chartofaccount.models import Chartofaccount
from subledger.models import Subledger
from subledgersummary.models import Subledgersummary
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from companyparameter.models import Companyparameter
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.http import JsonResponse
from django.db import connection
from collections import namedtuple
import datetime
import pandas as pd
from datetime import timedelta
import io
from xlsxwriter.workbook import Workbook


@method_decorator(login_required, name='dispatch')
class IndexView(TemplateView):
    template_name = 'generalledgerbook/index.html'

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        months = ([0, '***** Year End *****'], [1, 'January'], [2, 'February'], [3, 'March'], [4, 'April'], [5, 'May'], [6 ,'June'], \
                  [7, 'July'], [8, 'August'], [9, 'September'], [10, 'October'], [11, 'November'], [12, 'December'])

        context['months'] = months
        today = datetime.datetime.now()
        context['this_month'] = 1#today.month
        context['this_year'] = today.year

        return context

@csrf_exempt
def pdf(request):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return response

@csrf_exempt
def excel(request):
    # request variables
    report = request.GET["report"]
    type = request.GET["type"]
    year = request.GET["year"]
    month = request.GET["month"]

    prevdate = datetime.date(int(year), int(month), 10) - timedelta(days=15)
    prevyear = prevdate.year
    prevmonth = prevdate.month

    # RETAINED EARNINGS
    retained_earnings = Companyparameter.objects.first().coa_retainedearnings_id
    current_earnings = Companyparameter.objects.first().coa_currentearnings_id

    if report == 'TB':
        result = query_trial_balance(retained_earnings, current_earnings, year, month, prevyear, prevmonth)
        return excel_trail_balance(result, report, type, year, month)
    elif report == 'BS':
        result = query_balance_sheet(retained_earnings, current_earnings, year, month, prevyear, prevmonth)
        current_month = datetime.date(int(year), int(month), 10).strftime("%B")
        prev_month = datetime.date(int(prevyear), int(prevmonth), 10).strftime("%B")
        return excel_balance_sheet(result, report, type, year, month, current_month, prev_month)
    elif report == 'IS':
        result = query_balance_sheet(retained_earnings, current_earnings, year, month, prevyear, prevmonth)
        return excel_balance_sheet(result, report, type, year, month)
    else:
        print "no report"

@csrf_exempt
def generate(request):

    report = request.GET["report"]
    type = request.GET["type"]
    year = request.GET["year"]
    month = request.GET["month"]

    prevdate = datetime.date(int(year), int(month), 10) - timedelta(days=15)
    prevyear = prevdate.year
    prevmonth = prevdate.month

    # RETAINED EARNINGS
    retained_earnings = Companyparameter.objects.first().coa_retainedearnings_id
    current_earnings = Companyparameter.objects.first().coa_currentearnings_id

    context = {}

    if report == 'TB':
        print "trial balance"
        context['month'] = datetime.date(int(year), int(month), 10).strftime("%B")
        context['year'] = year
        context['result'] = query_trial_balance(retained_earnings, current_earnings, year, month, prevyear, prevmonth)
        viewhtml = render_to_string('generalledgerbook/trial_balance.html', context)
    elif report == 'BS':
        print "balance sheet"
        context['month'] = datetime.date(int(year), int(month), 10).strftime("%B")
        context['prev_month'] = datetime.date(int(prevyear), int(prevmonth), 10).strftime("%B")
        context['result'] = query_balance_sheet(retained_earnings, current_earnings, year, month, prevyear, prevmonth)
        viewhtml = render_to_string('generalledgerbook/balance_sheet.html', context)
    elif report == 'IS':
        print "income statement"
        result = query_income_statement(retained_earnings, current_earnings, year, month, prevyear, prevmonth)
        dataset = pd.DataFrame(result)
        cur_netsales = dataset.groupby('group_code')['current_amount'].sum()
        prev_netsales = dataset.groupby('group_code')['prev_amount'].sum()
        context['cur_netsales'] = float(format(cur_netsales['GS'], '.2f'))
        context['prev_netsales'] = float(format(prev_netsales['GS'], '.2f'))
        context['month'] = datetime.date(int(year), int(month), 10).strftime("%B")
        context['prev_month'] = datetime.date(int(prevyear), int(prevmonth), 10).strftime("%B")
        context['result'] = result
        #test = dataset.groupby(['group_code']).sum().sum(level=['group_code']).unstack('Groups').fillna(0).reset_index()
        #print test
        viewhtml = render_to_string('generalledgerbook/income_statement.html', context)
    else:
        print "no report"

    data = {
        'status': 'success',
        'viewhtml': viewhtml,
    }
    return JsonResponse(data)

def query_trial_balance(retained_earnings, current_earnings, year, month, prevyear, prevmonth):
    print "trial balance query"
    ''' Create query '''
    cursor = connection.cursor()
    query = "SELECT  chart.id AS chartid, chart.main AS chartmain, maingroup.code AS maingroup_code, maingroup.description AS maingroup_desc, " \
             "subgroup.code AS subgroup_code, subgroup.description AS subgroup_desc," \
             "chart.accountcode, chart.description, chart.balancecode, " \
             "chart.beginning_amount, chart.beginning_code, IFNULL(chart.end_amount, 0) AS end_amount, " \
             "chart.end_code, IFNULL(chart.year_to_date_amount, 0) AS year_to_date_amount, chart.year_to_date_code, " \
             "IF (chart.id = " + str(retained_earnings) + " AND summary.month = 12, IFNULL(chart.beginning_amount, 0) , IFNULL(summary.end_amount, 0)) AS summary_end_amount, " \
             "IF (chart.id = " + str(retained_earnings) + " AND summary.month = 12, chart.beginning_code , summary.end_code) AS summary_end_code, " \
             "IF (chart.main >= 4 AND summary.month = 12, IFNULL(chart.beginning_amount, 0), IFNULL(summary.year_to_date_amount, 0)) " \
             "AS summary_year_to_date_amount, " \
             "IF (chart.main >= 4 AND summary.month = 12, chart.beginning_code, summary.year_to_date_code) AS summary_year_to_date_code, " \
             "subled_d.balancecode AS debit_code, IFNULL(subled_d.amount, 0) AS debit_amount, " \
             "subled_c.balancecode AS credit_code, IFNULL(subled_c.amount, 0) AS credit_amount, " \
             "IF (IFNULL(subled_d.amount, 0) >= IFNULL(subled_c.amount, 0), 'D', 'C') AS trans_mon_code, " \
             "ABS(IFNULL(subled_d.amount, 0) - IFNULL(subled_c.amount, 0)) AS trans_mon_amount " \
             "FROM chartofaccount AS chart " \
             "LEFT OUTER JOIN (" \
             "   SELECT summary.chartofaccount_id, " \
             "   summary.beginning_amount AS summary_beg_amount, summary.beginning_code AS summary_beg_code,	" \
             "   summary.end_amount, summary.end_code, " \
             "   summary.year_to_date_amount, summary.year_to_date_code, summary.month " \
             "   FROM subledgersummary AS summary " \
             "   WHERE summary.year = '" + str(prevyear) + "' AND summary.month = '" + str(prevmonth) + "' " \
             ") AS summary ON summary.chartofaccount_id = chart.id " \
             "LEFT OUTER JOIN ( " \
             "  SELECT subled.chartofaccount_id, subled.balancecode, SUM(amount) AS amount " \
             "  FROM subledger AS subled " \
             "  WHERE YEAR(subled.document_date) = '" + str(year) + "' AND MONTH(subled.document_date) = '" + str(month) + "' " \
             "  AND subled.balancecode = 'D' " \
             "  GROUP BY subled.chartofaccount_id, subled.balancecode " \
             ") AS subled_d ON subled_d.chartofaccount_id = chart.id " \
             "LEFT OUTER JOIN ( " \
             "  SELECT subled.chartofaccount_id, subled.balancecode, SUM(amount) AS amount " \
             "  FROM subledger AS subled " \
             "  WHERE YEAR(subled.document_date) = '" + str(year) + "' AND MONTH(subled.document_date) = '" + str(month) + "' " \
             "  AND subled.balancecode = 'C' " \
             "  GROUP BY subled.chartofaccount_id, subled.balancecode " \
             ") AS subled_c ON subled_c.chartofaccount_id = chart.id " \
             "LEFT OUTER JOIN chartofaccountsubgroup AS subgroup ON subgroup.id = chart.subgroup_id " \
             "LEFT OUTER JOIN chartofaccountmainsubgroup AS mainsubgroup ON mainsubgroup.sub_id = subgroup.id " \
             "LEFT OUTER JOIN chartofaccountmaingroup AS maingroup ON maingroup.id = mainsubgroup.main_id " \
             "WHERE chart.accounttype = 'P' AND chart.isdeleted = 0 AND chart.id != " + str(current_earnings) + " " \
             "ORDER BY chart.accountcode ASC"

    cursor.execute(query)
    result = namedtuplefetchall(cursor)

    return result

def query_balance_sheet(retained_earnings, current_earnings, year, month, prevyear, prevmonth):
    print "balance sheet query"
    ''' Create query '''
    cursor = connection.cursor()
    query = "SELECT z.*, " \
            "IF(z.current_code <>  z.main_balancecode, current_amount, ABS(current_amount)) AS current_amount_abs, " \
            "IF(z.prev_code <>  z.main_balancecode, prev_amount, ABS(prev_amount)) AS prev_amount_abs " \
            "FROM ( SELECT " \
            "       maingroup.balancecode AS main_balancecode, " \
            "       maingroup.code AS maingroup_code, maingroup.description AS maingroup_desc, " \
            "       subgroup.code AS subgroup_code, subgroup.description AS subgroup_desc, " \
            "       IF (maingroup.balancecode = 'C', (IFNULL(credit.credit_end_amount, 0) - IFNULL(debit.debit_end_amount, 0)) , (IFNULL(debit.debit_end_amount, 0) - IFNULL(credit.credit_end_amount, 0))) AS current_amount, " \
            "       IF (maingroup.balancecode = 'C', (IFNULL(summary_credit.sc_end_amount, 0) - IFNULL(summary_debit.sd_end_amount, 0)) , (IFNULL(summary_debit.sd_end_amount, 0) - IFNULL(summary_credit.sc_end_amount, 0))) AS prev_amount, " \
            "       IFNULL(debit.debit_end_code, 'D') AS debit_end_code, IFNULL(debit.debit_end_amount, 0) AS debit_end_amount, " \
            "       IFNULL(credit.credit_end_code, 'C') AS credit_end_code, IFNULL(credit.credit_end_amount, 0) AS credit_end_amount, " \
            "       IFNULL(summary_debit.sd_end_code, 'D') AS sd_end_code, IFNULL(summary_debit.sd_end_amount, 'D') AS sd_end_amount, " \
            "       IFNULL(summary_credit.sc_end_code, 'C')AS sc_end_code, IFNULL(summary_credit.sc_end_amount, 'C') AS sc_end_amount," \
            "       IF (IFNULL(debit.debit_end_amount, 0) >= IFNULL(credit.credit_end_amount, 0), IFNULL(debit.debit_end_code, 'D'), IFNULL(credit.credit_end_code, 'C')) AS current_code, " \
            "       IF (IFNULL(summary_debit.sd_end_amount, 0) >= IFNULL(summary_credit.sc_end_amount, 0), IFNULL(summary_debit.sd_end_code, 'D'), IFNULL(summary_credit.sc_end_code, 'C')) AS prev_code " \
            "FROM chartofaccount AS chart " \
            "LEFT OUTER JOIN chartofaccountsubgroup AS subgroup ON subgroup.id = chart.subgroup_id " \
            "LEFT OUTER JOIN chartofaccountmainsubgroup AS mainsubgroup ON mainsubgroup.sub_id = subgroup.id " \
            "LEFT OUTER JOIN chartofaccountmaingroup AS maingroup ON maingroup.id = mainsubgroup.main_id " \
            "LEFT OUTER JOIN ( " \
            "   SELECT chart_d.id AS debit_id, SUM(chart_d.end_amount) AS debit_end_amount, chart_d.end_code AS debit_end_code, " \
            "           subgroup_d.id AS debit_subgroup, subgroup_d.code AS debit_subgroupcode " \
            "   FROM chartofaccount AS chart_d " \
            "   LEFT OUTER JOIN chartofaccountsubgroup AS subgroup_d ON subgroup_d.id = chart_d.subgroup_id " \
            "   WHERE chart_d.end_code = 'D' AND chart_d.accounttype = 'P' AND chart_d.isdeleted = 0 AND chart_d.main <= 3 AND chart_d.id != '"+str(current_earnings)+"' " \
            "   GROUP BY subgroup_d.id, chart_d.end_code " \
            "   UNION " \
            "   SELECT chart_d.id AS debit_id, SUM(chart_d.year_to_date_amount) AS debit_end_amount, chart_d.end_code AS debit_end_code, " \
            "           subgroup_d.id AS debit_subgroup, subgroup_d.code AS debit_subgroupcode " \
            "   FROM chartofaccount AS chart_d " \
            "   LEFT OUTER JOIN chartofaccountsubgroup AS subgroup_d ON subgroup_d.id = '164' " \
            "   WHERE chart_d.end_code = 'D' AND chart_d.accounttype = 'P' AND chart_d.isdeleted = 0 AND chart_d.main > 3 " \
            ") AS debit ON debit.debit_subgroup = subgroup.id " \
            "LEFT OUTER JOIN ( " \
            "   SELECT chart_c.id AS credit_id, SUM(chart_c.end_amount) AS credit_end_amount, chart_c.end_code AS credit_end_code, " \
            "           subgroup_c.id AS credit_subgroup, subgroup_c.code AS credit_subgroupcode " \
            "   FROM chartofaccount AS chart_c " \
            "   LEFT OUTER JOIN chartofaccountsubgroup AS subgroup_c ON subgroup_c.id = chart_c.subgroup_id " \
            "   WHERE chart_c.end_code = 'C' AND chart_c.accounttype = 'P' AND chart_c.isdeleted = 0 AND chart_c.main <= 3 AND chart_c.id != '"+str(current_earnings)+"' " \
            "   GROUP BY subgroup_c.id, chart_c.end_code " \
            "   UNION " \
            "   SELECT chart_c.id AS credit_id, SUM(chart_c.year_to_date_amount) AS credit_end_amount, chart_c.end_code AS credit_end_code, " \
            "           subgroup_c.id AS credit_subgroup, subgroup_c.code AS credit_subgroupcode " \
            "   FROM chartofaccount AS chart_c " \
            "   LEFT OUTER JOIN chartofaccountsubgroup AS subgroup_c ON subgroup_c.id = '164' " \
            "   WHERE chart_c.end_code = 'C' AND chart_c.accounttype = 'P' AND chart_c.isdeleted = 0 AND chart_c.main > 3 " \
            ") AS credit ON credit.credit_subgroup = subgroup.id " \
            "LEFT OUTER JOIN ( " \
            "   SELECT subgroup.id AS s_debit_id, subgroup.code AS s_debit_code, " \
            "           SUM(summary.end_amount) AS sd_end_amount, summary.end_code AS sd_end_code " \
            "   FROM subledgersummary AS summary " \
            "   LEFT OUTER JOIN chartofaccount AS chart ON chart.id = summary.chartofaccount_id " \
            "   LEFT OUTER JOIN chartofaccountsubgroup AS subgroup ON subgroup.id = chart.subgroup_id " \
            "   WHERE summary.year = '" + str(prevyear) + "' AND summary.month = '" + str(prevmonth) + "' AND summary.end_code = 'D' " \
            "   AND chart.accounttype = 'P' AND chart.isdeleted = 0 AND chart.main <= 3 AND chart.id != '"+str(current_earnings)+"' " \
            "   GROUP BY subgroup.id, summary.end_code " \
            "   UNION " \
            "   SELECT subgroup.id AS s_debit_id, subgroup.code AS s_debit_code, " \
            "           SUM(summary.end_amount) AS sd_end_amount, summary.end_code AS sd_end_code " \
            "   FROM subledgersummary AS summary " \
            "   LEFT OUTER JOIN chartofaccount AS chart ON chart.id = summary.chartofaccount_id " \
            "   LEFT OUTER JOIN chartofaccountsubgroup AS subgroup ON subgroup.id = chart.subgroup_id " \
            "   WHERE summary.year = '" + str(prevyear) + "' AND summary.month = '" + str(prevmonth) + "' AND summary.end_code = 'D' " \
            "   AND chart.accounttype = 'P' AND chart.isdeleted = 0 AND chart.id = '" + str(current_earnings) + "' " \
            "   GROUP BY subgroup.id, summary.end_code " \
            ") AS summary_debit ON summary_debit.s_debit_id = subgroup.id " \
            "LEFT OUTER JOIN ( " \
            "   SELECT subgroup.id AS s_credit_id, subgroup.code AS s_credit_code, " \
            "           SUM(summary.end_amount) AS sc_end_amount, summary.end_code AS sc_end_code " \
            "   FROM subledgersummary AS summary " \
            "   LEFT OUTER JOIN chartofaccount AS chart ON chart.id = summary.chartofaccount_id " \
            "   LEFT OUTER JOIN chartofaccountsubgroup AS subgroup ON subgroup.id = chart.subgroup_id " \
            "   WHERE summary.year = '" + str(prevyear) + "' AND summary.month = '" + str(prevmonth) + "' AND summary.end_code = 'C' " \
            "   AND chart.accounttype = 'P' AND chart.isdeleted = 0 AND chart.main <= 3 AND chart.id != '"+str(current_earnings)+"' " \
            "   GROUP BY subgroup.id, summary.end_code " \
            "   UNION " \
            "   SELECT subgroup.id AS s_credit_id, subgroup.code AS s_credit_code, " \
            "           SUM(summary.end_amount) AS sc_end_amount, summary.end_code AS sc_end_code " \
            "   FROM subledgersummary AS summary " \
            "   LEFT OUTER JOIN chartofaccount AS chart ON chart.id = summary.chartofaccount_id " \
            "   LEFT OUTER JOIN chartofaccountsubgroup AS subgroup ON subgroup.id = chart.subgroup_id " \
            "   WHERE summary.year = '" + str(prevyear) + "' AND summary.month = '" + str(prevmonth) + "' AND summary.end_code = 'C' " \
            "   AND chart.accounttype = 'P' AND chart.isdeleted = 0 AND chart.id = '" + str(current_earnings) + "' " \
            "   GROUP BY subgroup.id, summary.end_code " \
            ") AS summary_credit ON summary_credit.s_credit_id = subgroup.id " \
            "WHERE chart.accounttype = 'P' AND chart.isdeleted = 0 AND chart.main <= 3 " \
            "GROUP BY subgroup.id " \
            "ORDER BY maingroup.code, subgroup.code) AS z"

    cursor.execute(query)
    result = namedtuplefetchall(cursor)

    return result

def query_income_statement(retained_earnings, current_earnings, year, month, prevyear, prevmonth):
    print "income statement query"
    ''' Create query '''
    cursor = connection.cursor()
    query = "SELECT grouping.code AS group_code, grouping.description AS group_desc, maingroup.code AS maingroup_code, maingroup.description AS maingroup_desc, " \
            "subgroup.code AS subgroup_code, subgroup.description AS subgroup_desc, " \
            "SUM(z.current_amount) AS current_amount, SUM(z.prev_amount) AS prev_amount, SUM(z.todate_amount) AS todate_amount " \
            "FROM ( " \
            "   SELECT chartmain.main, chartmain.balancecode, chart.id, chart.subgroup_id, chart.accountcode, chart.description, " \
            "   IF (chartmain.balancecode = 'D', (IFNULL(current_debit.end_amount, 0) - IFNULL(current_credit.end_amount, 0)), (IFNULL(current_credit.end_amount, 0) - IFNULL(current_debit.end_amount, 0))) AS current_amount, " \
            "   IF (chartmain.balancecode = 'D', (IFNULL(prev_debit.end_amount, 0) - IFNULL(prev_credit.end_amount, 0)), (IFNULL(prev_credit.end_amount, 0) - IFNULL(prev_debit.end_amount, 0))) AS prev_amount, " \
            "   IF (chartmain.balancecode = 'D', (IFNULL(todate_debit.year_to_date_amount, 0) - IFNULL(todate_credit.year_to_date_amount, 0)), (IFNULL(todate_credit.year_to_date_amount, 0) - IFNULL(todate_debit.year_to_date_amount, 0))) AS todate_amount, " \
            "   IFNULL(current_debit.end_amount, 0) AS current_debit_amount, " \
            "   IFNULL(current_debit.end_code, 'D') AS current_debit_code, " \
            "   IFNULL(current_credit.end_amount, 0) AS current_credit_amount, IFNULL(current_credit.end_code, 'C') AS current_credit_code, " \
            "   IFNULL(prev_debit.end_amount, 0) AS prev_debit_amount, IFNULL(prev_debit.end_code, 'D') AS prev_debit_code, " \
            "   IFNULL(prev_credit.end_amount, 0) AS prev_credit_amount, IFNULL(prev_credit.end_code, 'C') AS prev_credit_code, " \
            "   IFNULL(todate_debit.year_to_date_amount, 0) AS todate_debit_amount, IFNULL(todate_debit.year_to_date_code, 'D') AS todate_debit_code, " \
            "   IFNULL(todate_credit.year_to_date_amount, 0) AS todate_credit_amount, IFNULL(todate_credit.year_to_date_code, 'C') AS todate_credit_code " \
            "FROM chartofaccount AS chart " \
            "LEFT OUTER JOIN ( " \
            "   SELECT chart.id, chart.accountcode, chart.description, chart.end_amount, chart.end_code " \
            "   FROM chartofaccount AS chart " \
            "   WHERE chart.accounttype = 'P' AND chart.main > 3 " \
            "   AND chart.isdeleted = 0 AND chart.end_code = 'C' " \
            ") AS current_credit ON current_credit.id = chart.id " \
            "LEFT OUTER JOIN ( " \
            "   SELECT chart.id, chart.accountcode, chart.description, chart.end_amount, chart.end_code " \
            "   FROM chartofaccount AS chart " \
            "   WHERE chart.accounttype = 'P' AND chart.main > 3 " \
            "   AND chart.isdeleted = 0 AND chart.end_code = 'D' " \
            ") AS current_debit ON current_debit.id = chart.id " \
            "LEFT OUTER JOIN ( " \
            "   SELECT chart.id, chart.accountcode, summary.end_amount, summary.end_code " \
            "   FROM subledgersummary AS summary " \
            "   LEFT OUTER JOIN chartofaccount AS chart ON chart.id = summary.chartofaccount_id " \
            "   WHERE summary.year = '" + str(prevyear) + "' AND summary.month = '" + str(prevmonth) + "' AND summary.end_code = 'C' " \
            "   AND chart.accounttype = 'P' AND chart.main > 3 AND chart.isdeleted = 0 " \
            ") AS prev_credit ON prev_credit.id = chart.id " \
            "LEFT OUTER JOIN ( " \
            "   SELECT chart.id, chart.accountcode, summary.end_amount, summary.end_code " \
            "   FROM subledgersummary AS summary " \
            "   LEFT OUTER JOIN chartofaccount AS chart ON chart.id = summary.chartofaccount_id " \
            "   WHERE summary.year = '" + str(prevyear) + "' AND summary.month = '" + str(prevmonth) + "' AND summary.end_code = 'D' " \
            "   AND chart.accounttype = 'P' AND chart.main > 3 AND chart.isdeleted = 0 " \
            ") AS prev_debit ON prev_debit.id = chart.id " \
            "LEFT OUTER JOIN ( " \
            "   SELECT chart.id, chart.accountcode, chart.description, chart.year_to_date_amount, chart.year_to_date_code " \
            "   FROM chartofaccount AS chart " \
            "   WHERE chart.accounttype = 'P' AND chart.main > 3 " \
            "   AND chart.isdeleted = 0 AND chart.end_code = 'C' " \
            ") AS todate_credit ON todate_credit.id = chart.id " \
            "LEFT OUTER JOIN ( " \
            "   SELECT chart.id, chart.accountcode, chart.description, chart.year_to_date_amount, chart.year_to_date_code " \
            "   FROM chartofaccount AS chart " \
            "   WHERE chart.accounttype = 'P' AND chart.main > 3 " \
            "   AND chart.isdeleted = 0 AND chart.end_code = 'D' " \
            ") AS todate_debit ON todate_debit.id = chart.id " \
            "LEFT OUTER JOIN chartofaccount AS chartmain ON (IF(chartmain.main = 7,  " \
            "(chartmain.main = chart.main AND chartmain.clas = chart.clas AND chartmain.sub = 0  " \
            "AND chartmain.item = 0 AND chartmain.cont = 0 AND chartmain.sub = 000000) ,  " \
            "(chartmain.main = chart.main AND chartmain.clas = 0 AND chartmain.sub = 0  " \
            "AND chartmain.item = 0 AND chartmain.cont = 0 AND chartmain.sub = 000000))) " \
            "WHERE chart.accounttype = 'P' AND chart.isdeleted = 0 AND chart.main > 3 " \
            "ORDER BY chart.accountcode) AS z " \
            "LEFT OUTER JOIN chartofaccountsubgroup AS subgroup ON subgroup.id = z.subgroup_id " \
            "LEFT OUTER JOIN chartofaccountmainsubgroup AS mainsubgroup ON mainsubgroup.sub_id = subgroup.id " \
            "LEFT OUTER JOIN chartofaccountmaingroup AS maingroup ON maingroup.id = mainsubgroup.main_id " \
            "LEFT OUTER JOIN chartofaccountmaingroup AS grouping ON grouping.id = maingroup.group_id " \
            "GROUP BY maingroup.code, subgroup.code " \
            "ORDER BY maingroup.code, subgroup.code"

    cursor.execute(query)
    result = namedtuplefetchall(cursor)

    return result

def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def excel_trail_balance(result, report, type, year, month):
    mon = datetime.date(int(year), int(month), 10).strftime("%B")
    if type == 'P':
        type = 'preliminary'
    else:
        type = 'final'

    file_name = "trial_balance_"+type+"_"+year+"_"+mon+".xlsx"

    output = io.BytesIO()

    workbook = Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    # variables
    bold = workbook.add_format({'bold': 1})

    # header
    worksheet.write('A1', 'Account Code', bold)
    worksheet.write('B1', 'Chart of Account', bold)
    worksheet.write('C1', 'Beg Debit', bold)
    worksheet.write('D1', 'Beg Credit', bold)
    worksheet.write('E1', 'Mon Debit', bold)
    worksheet.write('F1', 'Mon Credit', bold)
    worksheet.write('G1', 'End Debit', bold)
    worksheet.write('H1', 'End Credit', bold)
    worksheet.write('I1', 'Inc Debit', bold)
    worksheet.write('J1', 'Inc Credit', bold)
    worksheet.write('K1', 'Bal Debit', bold)
    worksheet.write('L1', 'Bal Credit', bold)
    worksheet.write('M1', 'Main Group Code', bold)
    worksheet.write('N1', 'Main Group Description', bold)
    worksheet.write('O1', 'Sub Group Code', bold)
    worksheet.write('P1', 'Sub Group Description', bold)

    # Start from the first cell. Rows and columns are zero indexed.
    row = 1
    col = 0
    total_beg_debit = 0
    total_beg_credit = 0
    total_mon_debit = 0
    total_mon_credit = 0
    total_end_debit = 0
    total_end_credit = 0
    subtotal_inc_debit = 0
    subtotal_inc_credit = 0
    subtotal_bal_debit = 0
    subtotal_bal_credit = 0
    current_inc_debit = 0
    current_inc_credit = 0
    current_bal_debit = 0
    current_bal_credit = 0
    total_inc_debit = 0
    total_inc_credit = 0
    total_bal_debit = 0
    total_bal_credit = 0

    # Iterate over the data and write it out row by row.
    for data in result:
        worksheet.write(row, col, data.accountcode)
        worksheet.write(row, col + 1, data.description)

        if data.chartmain <= 3:
            if data.summary_end_code == 'D':
                worksheet.write(row, col + 2, float(format(data.summary_end_amount, '.2f')))
                worksheet.write(row, col + 3, float(format(0.00, '.2f')))
                total_beg_debit += float(format(data.summary_end_amount, '.2f'))
            else:
                worksheet.write(row, col + 2, float(format(0.00, '.2f')))
                worksheet.write(row, col + 3, float(format(data.summary_end_amount, '.2f')))
                total_beg_credit += float(format(data.summary_end_amount, '.2f'))
        else:
            if data.summary_end_code == 'D':
                worksheet.write(row, col + 2, float(format(data.summary_year_to_date_amount, '.2f')))
                worksheet.write(row, col + 3, float(format(0.00, '.2f')))
                total_beg_debit += float(format(data.summary_year_to_date_amount, '.2f'))
            else:
                worksheet.write(row, col + 2, float(format(0.00, '.2f')))
                worksheet.write(row, col + 3, float(format(data.summary_year_to_date_amount, '.2f')))
                total_beg_credit += float(format(data.summary_year_to_date_amount, '.2f'))

        if data.trans_mon_code == 'D':
            worksheet.write(row, col + 4, float(format(data.trans_mon_amount, '.2f')))
            worksheet.write(row, col + 5, float(format(0.00, '.2f')))
            total_mon_debit += float(format(data.trans_mon_amount, '.2f'))
        else:
            worksheet.write(row, col + 4, float(format(0.00, '.2f')))
            worksheet.write(row, col + 5, float(format(data.trans_mon_amount, '.2f')))
            total_mon_credit += float(format(data.trans_mon_amount, '.2f'))

        if data.chartmain <= 3:
            if data.end_code == 'D':
                worksheet.write(row, col + 6, float(format(data.end_amount, '.2f')))
                worksheet.write(row, col + 7, float(format(0.00, '.2f')))
                worksheet.write(row, col + 8, float(format(0.00, '.2f')))
                worksheet.write(row, col + 9, float(format(0.00, '.2f')))
                worksheet.write(row, col + 10, float(format(data.end_amount, '.2f')))
                worksheet.write(row, col + 11, float(format(0.00, '.2f')))
                total_end_debit += float(format(data.end_amount, '.2f'))
                subtotal_bal_debit += float(format(data.end_amount, '.2f'))
            else:
                worksheet.write(row, col + 6, float(format(0.00, '.2f')))
                worksheet.write(row, col + 7, float(format(data.end_amount, '.2f')))
                worksheet.write(row, col + 8, float(format(0.00, '.2f')))
                worksheet.write(row, col + 9, float(format(0.00, '.2f')))
                worksheet.write(row, col + 10, float(format(0.00, '.2f')))
                worksheet.write(row, col + 11, float(format(data.end_amount, '.2f')))
                total_end_credit += float(format(data.end_amount, '.2f'))
                subtotal_bal_credit += float(format(data.end_amount, '.2f'))
        else:
            if data.end_code == 'D':
                worksheet.write(row, col + 6, float(format(data.year_to_date_amount, '.2f')))
                worksheet.write(row, col + 7, float(format(0.00, '.2f')))
                worksheet.write(row, col + 8, float(format(data.year_to_date_amount, '.2f')))
                worksheet.write(row, col + 9, float(format(0.00, '.2f')))
                worksheet.write(row, col + 10, float(format(0.00, '.2f')))
                worksheet.write(row, col + 11, float(format(0.00, '.2f')))
                total_end_debit += float(format(data.year_to_date_amount, '.2f'))
                subtotal_inc_debit += float(format(data.year_to_date_amount, '.2f'))
            else:
                worksheet.write(row, col + 6, float(format(0.00, '.2f')))
                worksheet.write(row, col + 7, float(format(data.year_to_date_amount, '.2f')))
                worksheet.write(row, col + 8, float(format(0.00, '.2f')))
                worksheet.write(row, col + 9, float(format(data.year_to_date_amount, '.2f')))
                worksheet.write(row, col + 10, float(format(0.00, '.2f')))
                worksheet.write(row, col + 11, float(format(0.00, '.2f')))
                total_end_credit += float(format(data.year_to_date_amount, '.2f'))
                subtotal_inc_credit += float(format(data.year_to_date_amount, '.2f'))

        worksheet.write(row, col + 12, data.maingroup_code)
        worksheet.write(row, col + 13, data.maingroup_desc)
        worksheet.write(row, col + 14, data.subgroup_code)
        worksheet.write(row, col + 15, data.subgroup_desc)
        row += 1

    # Write a total using a formula. subtotal
    worksheet.write(row, 0, 'Subtotal')
    worksheet.write(row, col + 8, float(format(subtotal_inc_debit, '.2f')))
    worksheet.write(row, col + 9, float(format(subtotal_inc_credit, '.2f')))
    worksheet.write(row, col + 10, float(format(subtotal_bal_debit, '.2f')))
    worksheet.write(row, col + 11, float(format(subtotal_bal_credit, '.2f')))

    worksheet.write(row + 1, 0, 'Current Earnings/(loss)')
    if subtotal_inc_debit >= subtotal_inc_credit:
        current_inc_credit = float(format(subtotal_inc_debit, '.2f')) - float(format(subtotal_inc_credit, '.2f'))
        worksheet.write(row + 1, col + 8, float(format(0.00, '.2f')))
        worksheet.write(row + 1, col + 9, float(format(current_inc_credit, '.2f')))
    else:
        current_inc_debit = float(format(subtotal_inc_credit, '.2f')) - float(format(subtotal_inc_debit, '.2f'))
        worksheet.write(row + 1, col + 8, float(format(current_inc_debit, '.2f')))
        worksheet.write(row + 1, col + 9, float(format(0.00, '.2f')))

    if subtotal_bal_debit >= subtotal_bal_credit:
        current_bal_credit = float(format(subtotal_bal_debit, '.2f')) - float(format(subtotal_bal_credit, '.2f'))
        worksheet.write(row + 1, col + 10, float(format(0.00, '.2f')))
        worksheet.write(row + 1, col + 11, float(format(current_bal_credit, '.2f')))
    else:
        current_bal_debit = float(format(subtotal_bal_credit, '.2f')) - float(format(subtotal_bal_debit, '.2f'))
        worksheet.write(row + 1, col + 10, float(format(current_bal_debit, '.2f')))
        worksheet.write(row + 1, col + 11, float(format(0.00, '.2f')))

    total_inc_debit = float(format(subtotal_inc_debit, '.2f')) + float(format(current_inc_debit, '.2f'))
    total_inc_credit = float(format(subtotal_inc_credit, '.2f')) + float(format(current_inc_credit, '.2f'))
    total_bal_debit = float(format(subtotal_bal_debit, '.2f')) + float(format(current_bal_debit, '.2f'))
    total_bal_credit = float(format(subtotal_bal_credit, '.2f')) + float(format(current_bal_credit, '.2f'))

    worksheet.write(row + 2, 0, 'Total')
    worksheet.write(row + 2, col + 2, float(format(total_beg_debit, '.2f')))
    worksheet.write(row + 2, col + 3, float(format(total_beg_credit, '.2f')))
    worksheet.write(row + 2, col + 4, float(format(total_mon_debit, '.2f')))
    worksheet.write(row + 2, col + 5, float(format(total_mon_credit, '.2f')))
    worksheet.write(row + 2, col + 6, float(format(total_end_debit, '.2f')))
    worksheet.write(row + 2, col + 7, float(format(total_end_credit, '.2f')))
    worksheet.write(row + 2, col + 8, float(format(total_inc_debit, '.2f')))
    worksheet.write(row + 2, col + 9, float(format(total_inc_credit, '.2f')))
    worksheet.write(row + 2, col + 10, float(format(total_bal_debit, '.2f')))
    worksheet.write(row + 2, col + 11, float(format(total_bal_credit, '.2f')))
    # worksheet.write(row, 1, '=SUM(B1:B4)')
    workbook.close()

    output.seek(0)

    response = HttpResponse(output.read(),
                            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename="+file_name

    output.close()

    return response

def excel_balance_sheet(result, report, type, year, month, current_month, prev_month):

    mon = datetime.date(int(year), int(month), 10).strftime("%B")
    if type == 'P':
        type = 'preliminary'
    else:
        type = 'final'

    file_name = "balance_sheet_" + type + "_" + year + "_" + mon + ".xlsx"

    output = io.BytesIO()

    workbook = Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    # variables
    bold = workbook.add_format({'bold': 1})
    cell_format = workbook.add_format()
    cell_format.set_align('right')
    #right = workbook.add_format({'right': 1}).set_align('right')

    # header
    worksheet.merge_range('A1:C1', 'PHILIPPINE DAILY INQUIRER, INC.', bold)
    worksheet.merge_range('A2:C2', 'BALANCE SHEET', bold)
    worksheet.merge_range('A3:C3', 'AS OF '+str(current_month).upper()+' & '+str(prev_month).upper()+' '+str(year), bold)
    worksheet.write('D4', current_month, bold)
    worksheet.write('E4', prev_month, bold)
    worksheet.write('F4', current_month +' %', bold)
    worksheet.write('G4', prev_month +' %', bold)
    worksheet.write('H4', 'Variance', bold)
    worksheet.write('I4', '%', bold)

    row = 4
    col = 0
    current_percentage = 0
    prev_percentage = 0
    variance_percentage = 0
    variance = 0

    dataset = pd.DataFrame(result)
    total_current = dataset['current_amount_abs'].sum()
    total_previous = dataset['prev_amount_abs'].sum()
    for maingroup, subgroup in dataset.groupby(['maingroup_code', 'maingroup_desc']):
        #print subgroup['current_amount_abs']
        worksheet.write(row, col, str(maingroup[1]), bold)
        row += 1
        subtotal_current = 0
        subtotal_previous = 0
        subtotal_variance = 0
        subtotal_cur = subgroup.groupby('maingroup_code')['current_amount_abs'].sum()
        subtotal_prev = subgroup.groupby('maingroup_code')['prev_amount_abs'].sum()

        for data, sub in subgroup.iterrows():
            worksheet.write(row, col, str(sub['subgroup_code']))
            worksheet.write(row, col+1, str(sub['subgroup_desc']))
            worksheet.write(row, col+3, float(format(sub['current_amount_abs'], '.2f')))
            worksheet.write(row, col+4, float(format(sub['prev_amount_abs'], '.2f')))

            current_percentage = float(format(sub['current_amount_abs'], '.2f')) / float(subtotal_cur) * 100
            previous_percentage = float(format(sub['prev_amount_abs'], '.2f')) / float(subtotal_prev) * 100

            variance = float(format(sub['current_amount_abs'], '.2f')) - float(format(sub['prev_amount_abs'], '.2f'))

            if float(variance) != 0:
                variance_percentage = float(variance) / float(format(sub['prev_amount_abs'], '.2f')) * 100
            else:
                variance_percentage = 0

            worksheet.write(row, col+5, float(format(current_percentage, '.2f')))
            worksheet.write(row, col+6, float(format(previous_percentage, '.2f')))
            worksheet.write(row, col+7, float(format(variance, '.2f')))
            worksheet.write(row, col+8, float(format(variance_percentage, '.2f')))

            subtotal_current += float(format(sub['current_amount_abs'], '.2f'))
            subtotal_previous += float(format(sub['prev_amount_abs'], '.2f'))
            subtotal_variance += float(format(variance, '.2f'))
            row += 1

        worksheet.write(row, col+1, 'TOTAL '+str(maingroup[1]), cell_format)
        worksheet.write(row, col+3, float(format(subtotal_current, '.2f')))
        worksheet.write(row, col+4, float(format(subtotal_previous, '.2f')))

        subtotal_current_percentage = float(format(subtotal_current, '.2f')) / float(total_current) * 100
        subtotal_previous_percentage = float(format(subtotal_previous, '.2f')) / float(total_previous) * 100
        subtotal_var = float(format(subtotal_variance, '.2f')) / float(format(subtotal_previous, '.2f')) * 100

        worksheet.write(row, col+5, float(format(subtotal_current_percentage, '.2f')))
        worksheet.write(row, col+6, float(format(subtotal_previous_percentage, '.2f')))
        worksheet.write(row, col+7, float(format(subtotal_current, '.2f')) - float(format(subtotal_previous, '.2f')))
        worksheet.write(row, col+8, float(format(subtotal_var, '.2f')))
        row += 1
        #worksheet.write(row_main, col, str(maingroup[1]))
        #row_main += 1
        #print subgroup
        #for data, sub in subgroup.iterrows():
        #    worksheet.write(row, col, str(sub['subgroup_code']))
        #    worksheet.write(row, col+1, str(sub['subgroup_desc']))
        #    row += 1
    worksheet.write(row+1, col+1, 'TOTAL LIABILITIES & EQUITY', cell_format)
    worksheet.write(row+1, col+3, float(format(total_current, '.2f')))
    worksheet.write(row+1, col+4, float(format(total_previous, '.2f')))
    worksheet.write(row+1, col+5, float(0.00))
    worksheet.write(row+1, col+6, float(0.00))
    worksheet.write(row+1, col+7, float(format(total_current, '.2f')) - float(format(total_previous, '.2f')))
    total_var_percentage = (float(format(total_current, '.2f')) - float(format(total_previous, '.2f'))) / float(format(total_previous, '.2f')) * 100
    worksheet.write(row+1, col+8, float(format(total_var_percentage, '.2f')))

    workbook.close()

    output.seek(0)

    response = HttpResponse(output.read(),
                            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=" + file_name

    output.close()

    return response

