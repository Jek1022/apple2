from django.views.generic import ListView, TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from chartofaccount.models import Chartofaccount
from companyparameter.models import Companyparameter
from easy_pdf.views import PDFTemplateView
from django.core import serializers
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import xlwt


# initial setup
model_initial = Chartofaccount
template_initial = 'rep_chartofaccount/'
title_initial = 'Report - Chart of Account'
system_version = 'IES Financial System (ver 0.1)'

all_header = [["accountcode", "Account Code"], ["title", "Title"], ["description", "Description"]]
default_header = [["accountcode", "Account Code"], ["title", "Title"], ["description", "Description"]]

xls_sheetname_initial = 'Chart of account'


@method_decorator(login_required, name='dispatch')
class IndexView(ListView):
    model = model_initial
    template_name = template_initial + 'index.html'
    context_object_name = 'data_list'

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['title_initial'] = title_initial
        context['list_header'] = default_header
        context['all_header'] = all_header

        return context


@csrf_exempt
def report(request):

    if request.method == 'POST':

        list_table = model_initial.objects

        list_header = []
        list_header_modified = []
        for i in default_header:
            list_header.append(i[0])
            list_header_modified.append(i[1])

        if request.POST.getlist('list_header[]'):
            list_header = request.POST.getlist('list_header[]')

            list_header_modified = []
            for i in list_header:
                for j in default_header:
                    if j[0] == i:
                        list_header_modified.append(j[1])
                        print list_header_modified

        if request.POST['from']:
            date_from = datetime.combine(datetime.strptime(request.POST['from'], '%Y-%m-%d'), datetime.min.time())
            list_table = list_table.filter(Q(enterdate__gt=date_from))

        if request.POST['to']:
            date_to = datetime.combine(datetime.strptime(request.POST['to'], '%Y-%m-%d'), datetime.max.time())
            list_table = list_table.filter(Q(enterdate__lt=date_to))

        if request.POST.getlist('orderby[]') and request.POST['orderasc']:
            orderby = request.POST.getlist('orderby[]')
            orderasc = request.POST['orderasc']

            list_table.order_by(*orderby)

            if orderasc == 'a':
                list_table = list_table.reverse()

        if request.POST.getlist('advanced_filter[]') and request.POST.getlist('advanced_keyword[]'):
            advanced_filter = request.POST.getlist('advanced_filter[]')
            advanced_keyword = request.POST.getlist('advanced_keyword[]')

            arg = {}
            q_objects = Q()

            for index, data in enumerate(advanced_filter):
                if data and advanced_keyword[index]:
                    arg['{0}__{1}'.format(data, 'contains')] = advanced_keyword[index]
                    for data in arg.iteritems():
                        # fix bloated for loop
                        q_objects.add(Q(data), Q.OR)

            list_table = list_table.filter(q_objects)

        list_table = list_table.only(*list_header).filter(isdeleted=0)[0:10]

        data = {
            'status': 'success',
            'list_table': serializers.serialize('json', list_table),
            'list_header': list_header,
            'list_header_modified': list_header_modified,
        }
    else:
        data = {
            'status': 'error',
        }

    return JsonResponse(data)


@method_decorator(login_required, name='dispatch')
class Pdf(PDFTemplateView):
    model = model_initial
    template_name = template_initial + 'pdf.html'

    def get_context_data(self, **kwargs):
        context = super(Pdf, self).get_context_data(**kwargs)
        context['companyparameter'] = Companyparameter.objects.get(code='PDI', isdeleted=0)

        context['list_header'] = []
        context['custom_header'] = []
        list_header = []
        for i in default_header:
            context['list_header'].append(i[0])
            list_header.append(i[0])
            context['custom_header'].append(i[1])

        context['user'] = self.request.user
        context['pagesize'] = "a4"
        context['fontsize'] = "10"
        context['logo'] = "http://" + self.request.META['HTTP_HOST'] + "/static/images/my-inquirer-logo.png"
        context['title'] = title_initial
        context['date_from'] = datetime.strptime('1990-01-01', '%Y-%m-%d').strftime("%B %d, %Y")
        context['date_to'] = datetime.now().strftime("%B %d, %Y")
        context['system_version'] = system_version

        try:
            list_table = model_initial.objects
            context['custom_header'] = default_header

            date_limit = datetime.combine(datetime.strptime('1990-01-01', '%Y-%m-%d'), datetime.min.time())

            if self.request.method == 'GET':

                if self.request.GET['title_initial']:
                    context['title'] = self.request.GET['title_initial']

                if self.request.GET.getlist('list_header_modified'):
                    context['custom_header'] = self.request.GET.getlist('list_header_modified')
                elif self.request.GET.getlist('list_header'):
                    context['custom_header'] = list_header

                if self.request.GET.getlist('list_header'):
                    list_header = self.request.GET.getlist('list_header')
                    context['list_header'] = list_header

                if self.request.GET['date_from']:
                    date_from = datetime.combine(datetime.strptime(self.request.GET['date_from'], '%Y-%m-%d'), datetime.min.time())

                    if date_from < datetime.now() and date_from > date_limit:
                        list_table = list_table.filter(Q(enterdate__gt=date_from))
                        context['date_from'] = datetime.strptime(self.request.GET['date_from'], '%Y-%m-%d').strftime("%B %d, %Y")

                if self.request.GET['date_to']:
                    date_to = datetime.combine(datetime.strptime(self.request.GET['date_to'], '%Y-%m-%d'), datetime.max.time())

                    if date_to < datetime.now() and date_to > date_limit:
                        list_table = list_table.filter(Q(enterdate__lt=date_to))
                        context['date_to'] = datetime.strptime(self.request.GET['date_to'], '%Y-%m-%d').strftime("%B %d, %Y")

                if self.request.GET.getlist('orderby') and self.request.GET['orderasc']:
                    orderby = self.request.GET.getlist('orderby')
                    orderasc = self.request.GET['orderasc']

                    list_table.order_by(*orderby)

                    if orderasc == 'a':
                        list_table = list_table.reverse()

                if self.request.GET.getlist('advanced_filter') and self.request.GET.getlist('advanced_keyword'):
                    advanced_filter = self.request.GET.getlist('advanced_filter')
                    advanced_keyword = self.request.GET.getlist('advanced_keyword')

                    arg = {}
                    q_objects = Q()

                    for index, data in enumerate(advanced_filter):
                        if data and advanced_keyword[index]:
                            arg['{0}__{1}'.format(data, 'contains')] = advanced_keyword[index].replace("+", " ")
                            for data in arg.iteritems():
                                q_objects.add(Q(data), Q.OR)

                    list_table = list_table.filter(q_objects)

                list_table = list_table.only(*list_header).filter(isdeleted=0)[0:10]

                if self.request.GET['orientation'] and self.request.GET['size']:
                    context['pagesize'] = self.request.GET['size'] + " " + self.request.GET['orientation']

                if self.request.GET['fontsize']:
                    context['fontsize'] = self.request.GET['fontsize'] + "px"

            context['data_list'] = list_table

        except ValueError:
            context['data_list'] = model_initial.objects.all()[0:0]

        return context


def xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="' + title_initial + '.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet(xls_sheetname_initial)

    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = []
    for i in default_header:
        columns.append(i[0])

    list_table = model_initial.objects
    rows = list_table
    date_limit = datetime.combine(datetime.strptime('1990-01-01', '%Y-%m-%d'), datetime.min.time())

    try:

        if request.method == 'GET':

            if request.GET['title_initial']:
                response['Content-Disposition'] = 'attachment; filename="' + request.GET['title_initial'] + '.xls"'

            if request.GET.getlist('list_header_modified'):
                custom_header = request.GET.getlist('list_header_modified')
            elif request.GET.getlist('list_header'):
                custom_header = columns
            for col_num in range(len(custom_header)):
                ws.write(row_num, col_num, custom_header[col_num], font_style)
            font_style = xlwt.XFStyle()

            if request.GET.getlist('list_header'):
                columns = request.GET.getlist('list_header')

            if request.GET['date_from']:
                date_from = datetime.combine(datetime.strptime(request.GET['date_from'], '%Y-%m-%d'), datetime.min.time())

                if date_from < datetime.now() and date_from > date_limit:
                    list_table = list_table.filter(Q(enterdate__gt=date_from))

            if request.GET['date_to']:
                date_to = datetime.combine(datetime.strptime(request.GET['date_to'], '%Y-%m-%d'), datetime.max.time())

                if date_to < datetime.now() and date_to > date_limit:
                    list_table = list_table.filter(Q(enterdate__lt=date_to))

            if request.GET.getlist('orderby') and request.GET['orderasc']:
                orderby = request.GET.getlist('orderby')
                orderasc = request.GET['orderasc']

                list_table.order_by(*orderby)

                if orderasc == 'a':
                    list_table = list_table.reverse()

            if request.GET.getlist('advanced_filter') and request.GET.getlist('advanced_keyword'):
                advanced_filter = request.GET.getlist('advanced_filter')
                advanced_keyword = request.GET.getlist('advanced_keyword')

                arg = {}
                q_objects = Q()

                for index, data in enumerate(advanced_filter):
                    if data and advanced_keyword[index]:
                        arg['{0}__{1}'.format(data, 'contains')] = advanced_keyword[index].replace("+", " ")
                        for data in arg.iteritems():
                            q_objects.add(Q(data), Q.OR)

                list_table = list_table.filter(q_objects)

            list_table = list_table.values_list(*columns).filter(isdeleted=0)[0:10]
            rows = list_table

    except ValueError:
            rows = model_initial.objects.all()[0:0]

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response
