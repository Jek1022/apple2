from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, JsonResponse, Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from . models import Prfmain
from requisitionform.models import Rfmain, Rfdetail
from purchaserequisitionform.models import Prfmain, Prfdetail, Prfdetailtemp, Rfprftransaction
from canvasssheet.models import Csmain, Csdetail, Csdata
from supplier.models import Supplier
from inventoryitemtype.models import Inventoryitemtype
from inventoryitem.models import Inventoryitem
from branch.models import Branch
from department.models import Department
from unitofmeasure.models import Unitofmeasure
from currency.models import Currency
from django.contrib.auth.models import User
from django.db.models import Q, F, Sum
from acctentry.views import generatekey
from easy_pdf.views import PDFTemplateView
import datetime

# pagination and search
from endless_pagination.views import AjaxListView


@method_decorator(login_required, name='dispatch')
class IndexView(AjaxListView):
    model = Prfmain
    template_name = 'purchaserequisitionform/index.html'
    context_object_name = 'data_list'

    # pagination and search
    page_template = 'purchaserequisitionform/index_list.html'
    def get_queryset(self):
        query = Prfmain.objects.all().filter(isdeleted=0)
        if self.request.COOKIES.get('keysearch_' + self.request.resolver_match.app_name):
            keysearch = str(self.request.COOKIES.get('keysearch_' + self.request.resolver_match.app_name))
            query = query.filter(Q(prfnum__icontains=keysearch) |
                                 Q(prfdate__icontains=keysearch) |
                                 Q(particulars__icontains=keysearch))
        return query


@method_decorator(login_required, name='dispatch')
class DetailView(DetailView):
    model = Prfmain
    template_name = 'purchaserequisitionform/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['prfdetail'] = Prfdetail.objects.filter(isdeleted=0, prfmain=self.kwargs['pk']).order_by('item_counter')
        context['totalpoquantity'] = Prfmain.objects.get(pk=self.kwargs['pk']).\
                                        totalquantity - Prfmain.objects.\
                                        get(pk=self.kwargs['pk']).totalremainingquantity
        return context


@method_decorator(login_required, name='dispatch')
class CreateView(CreateView):
    model = Prfmain
    template_name = 'purchaserequisitionform/create.html'
    fields = ['prfdate', 'inventoryitemtype', 'designatedapprover', 'prftype', 'particulars', 'branch', 'urgencytype', 'dateneeded']

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('purchaserequisitionform.add_prfmain'):
            raise Http404
        return super(CreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['secretkey'] = generatekey(self)
        context['inventoryitemtype'] = Inventoryitemtype.objects.filter(isdeleted=0)
        context['branch'] = Branch.objects.filter(isdeleted=0)
        context['department'] = Department.objects.filter(isdeleted=0).order_by('departmentname')
        context['invitem'] = Inventoryitem.objects.filter(isdeleted=0).order_by('inventoryitemclass__inventoryitemtype__code', 'description')
        context['rfmain'] = Rfmain.objects.filter(isdeleted=0, rfstatus='A', status='A')
        context['currency'] = Currency.objects.filter(isdeleted=0, status='A').order_by('id')
        context['unitofmeasure'] = Unitofmeasure.objects.filter(isdeleted=0).order_by('code')
        context['designatedapprover'] = User.objects.filter(is_active=1).exclude(username='admin').order_by('first_name')
        context['totalremainingquantity'] = 0
        return context

    def form_valid(self, form):
        if Prfdetailtemp.objects.filter(secretkey=self.request.POST['secretkey'], isdeleted=0):
            self.object = form.save(commit=False)

            year = str(form.cleaned_data['prfdate'].year)
            yearQS = Prfmain.objects.filter(prfnum__startswith=year)

            if yearQS:
                prfnumlast = yearQS.latest('prfnum')
                latestprfnum = str(prfnumlast)

                prfnum = year
                last = str(int(latestprfnum[4:])+1)
                zero_addon = 6 - len(last)
                for x in range(0, zero_addon):
                    prfnum += '0'
                prfnum += last

            else:
                prfnum = year + '000001'

            self.object.prfnum = prfnum
            self.object.branch = Branch.objects.get(pk=5)  # head office
            self.object.quantity = 0
            self.object.enterby = self.request.user
            self.object.modifyby = self.request.user
            self.object.save()

            itemquantity = 0
            detailtemp = Prfdetailtemp.objects.filter(isdeleted=0, secretkey=self.request.POST['secretkey']).order_by('enterdate')
            prfmain = Prfmain.objects.get(prfnum=prfnum)
            i = 1

            # delete and update of prfdetailtemp and prfdetail (respectively)
            for dt in detailtemp:

                department = Department.objects.get(pk=self.request.POST.getlist('temp_department')[i-1], isdeleted=0)

                detail = Prfdetail()
                detail.item_counter = i
                detail.prfmain = prfmain
                detail.invitem_code = dt.invitem_code
                detail.invitem_name = dt.invitem_name
                detail.invitem_unitofmeasure = Unitofmeasure.objects.get(code=self.request.POST.getlist('temp_item_um')[i-1], isdeleted=0, status='A')
                detail.invitem_unitofmeasure_code = Unitofmeasure.objects.get(code=self.request.POST.getlist('temp_item_um')[i-1], isdeleted=0, status='A').code
                detail.quantity = self.request.POST.getlist('temp_quantity')[i-1]
                detail.department = Department.objects.get(pk=self.request.POST.getlist('temp_department')[i-1])
                detail.department_code = department.code
                detail.department_name = department.departmentname
                detail.amount = 0
                detail.remarks = self.request.POST.getlist('temp_remarks')[i-1]
                detail.currency = Currency.objects.get(pk=self.request.POST.getlist('temp_item_currency')[i-1])
                detail.fxrate = self.request.POST.getlist('temp_fxrate')[i-1]
                detail.status = dt.status
                detail.enterby = dt.enterby
                detail.enterdate = dt.enterdate
                detail.modifyby = dt.modifyby
                detail.modifydate = dt.modifydate
                detail.postby = dt.postby
                detail.postdate = dt.postdate
                detail.isdeleted = dt.isdeleted
                detail.invitem = dt.invitem
                detail.rfmain = dt.rfmain
                detail.rfdetail = dt.rfdetail
                detail.poremainingquantity = self.request.POST.getlist('temp_quantity')[i-1]
                detail.save()
                dt.delete()

                if dt.rfmain:
                    if addRfprftransactionitem(detail.id):
                        itemquantity = int(itemquantity) + int(detail.quantity)
                    else:
                        detail.delete()
                else:
                    itemquantity = int(itemquantity) + int(detail.quantity)

                i += 1

            prfmain.quantity = int(itemquantity)
            prfmain.totalquantity = int(itemquantity)
            prfmain.totalremainingquantity = int(itemquantity)
            prfmain.save()

            return HttpResponseRedirect('/purchaserequisitionform/' + str(self.object.id) + '/update/')


def addRfprftransactionitem(id):
    prfdetail = Prfdetail.objects.get(pk=id)

    # validate quantity
    # print prfdetail.quantity
    # print prfdetail.rfdetail.prfremainingquantity
    # print prfdetail.rfdetail.isfullyprf
    if prfdetail.quantity <= prfdetail.rfdetail.prfremainingquantity and prfdetail.rfdetail.isfullyprf == 0:
        data = Rfprftransaction()
        data.rfmain = prfdetail.rfmain
        data.rfdetail = prfdetail.rfdetail
        data.prfmain = Prfdetail.objects.get(pk=id).prfmain
        data.prfdetail = Prfdetail.objects.get(pk=id)
        data.prfquantity = Prfdetail.objects.get(pk=id).quantity
        data.save()

        # adjust rf detail
        newprftotalquantity = prfdetail.rfdetail.prftotalquantity + data.prfquantity
        newprfremainingquantity = prfdetail.rfdetail.prfremainingquantity - data.prfquantity
        if newprfremainingquantity == 0:
            isfullyprf = 1
        else:
            isfullyprf = 0

        Rfdetail.objects.filter(pk=data.rfdetail.id).update(prftotalquantity=newprftotalquantity,
                                                            prfremainingquantity=newprfremainingquantity,
                                                            isfullyprf=isfullyprf)

        # adjust rf main
        rfmain_prfquantity = Rfmain.objects.get(pk=data.rfmain.id)
        newtotalremainingquantity = rfmain_prfquantity.totalremainingquantity - data.prfquantity
        Rfmain.objects.filter(pk=data.rfmain.id).update(totalremainingquantity=newtotalremainingquantity)

        return True

    else:
        return False


def deleteRfprftransactionitem(prfdetail):
    print prfdetail.id
    data = Rfprftransaction.objects.get(prfdetail=prfdetail.id, status='A')
    # update rfdetail
    remainingquantity = prfdetail.rfdetail.prfremainingquantity + data.prfquantity
    isfullyprf = 0 if remainingquantity != 0 else 1
    Rfdetail.objects.filter(pk=data.rfdetail.id).update(prftotalquantity=F('prftotalquantity')-data.prfquantity,
                                                        prfremainingquantity=F('prfremainingquantity')+data.prfquantity,
                                                        isfullyprf=isfullyprf)

    # update rfmain
    Rfmain.objects.filter(pk=data.rfmain.id).update(totalremainingquantity=F('totalremainingquantity')+data.prfquantity)

    # delete rfprftransaction, prfdetail
    data.delete()
    Prfdetail.objects.filter(pk=prfdetail.id).delete()
    Prfmain.objects.filter(pk=prfdetail.prfmain.id).update(quantity=0, grossamount=0.00,
                                                           netamount=0.00, vatable=0.00, vatamount=0.00,
                                                           vatexempt=0.00, vatzerorated=0.00)


class UpdateView(UpdateView):
    model = Prfmain
    template_name = 'purchaserequisitionform/edit.html'
    fields = ['prfnum', 'prfdate', 'inventoryitemtype', 'designatedapprover', 'prftype', 'particulars', 'branch', 'urgencytype', 'dateneeded']

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('purchaserequisitionform.change_prfmain'):
            raise Http404
        return super(UpdateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['secretkey'] = generatekey(self)
        context['inventoryitemtype'] = Inventoryitemtype.objects.filter(isdeleted=0)
        context['branch'] = Branch.objects.filter(isdeleted=0)
        context['department'] = Department.objects.filter(isdeleted=0).order_by('departmentname')
        context['invitem'] = Inventoryitem.objects.filter(isdeleted=0).order_by('inventoryitemclass__inventoryitemtype__code', 'description')
        context['rfmain'] = Rfmain.objects.filter(isdeleted=0, rfstatus='A', status='A')
        context['currency'] = Currency.objects.filter(isdeleted=0, status='A')
        context['unitofmeasure'] = Unitofmeasure.objects.filter(isdeleted=0).order_by('code')
        context['prfstatus'] = Prfmain.objects.get(pk=self.object.pk).get_prfstatus_display()
        context['designatedapprover'] = User.objects.filter(is_active=1).exclude(username='admin').order_by('first_name')
        context['totalremainingquantity'] = Prfmain.objects.get(pk=self.object.pk).\
            totalremainingquantity

        Prfdetailtemp.objects.filter(prfmain=self.object.pk).delete()        # clear all temp data

        detail = Prfdetail.objects.filter(isdeleted=0, prfmain=self.object.pk).order_by('item_counter')
        for d in detail:
            detailtemp = Prfdetailtemp()
            detailtemp.invitem_code = d.invitem_code
            detailtemp.invitem_name = d.invitem_name
            detailtemp.invitem_unitofmeasure = d.invitem_unitofmeasure
            detailtemp.invitem_unitofmeasure_code = d.invitem_unitofmeasure_code
            detailtemp.item_counter = d.item_counter
            detailtemp.quantity = d.quantity
            detailtemp.amount = d.amount
            detailtemp.department = d.department
            detailtemp.department_code = d.department_code
            detailtemp.department_name = d.department_name
            detailtemp.remarks = d.remarks
            detailtemp.currency = d.currency
            detailtemp.fxrate = d.fxrate
            detailtemp.status = d.status
            detailtemp.enterdate = d.enterdate
            detailtemp.modifydate = d.modifydate
            detailtemp.enterby = d.enterby
            detailtemp.modifyby = d.modifyby
            detailtemp.isdeleted = d.isdeleted
            detailtemp.postby = d.postby
            detailtemp.postdate = d.postdate
            detailtemp.invitem = d.invitem
            detailtemp.prfmain = d.prfmain
            detailtemp.rfmain = d.rfmain
            detailtemp.rfdetail = d.rfdetail
            detailtemp.isfullypo = d.isfullypo
            detailtemp.pototalquantity = d.pototalquantity
            detailtemp.poremainingquantity = d.poremainingquantity
            detailtemp.save()

        context['prfdetailtemp'] = Prfdetailtemp.objects.filter(isdeleted=0, prfmain=self.object.pk).order_by('item_counter')
        context['amount'] = []

        for data in context['prfdetailtemp']:
            amount = float(data.quantity) * float(data.invitem.unitcost)
            context['amount'].append(amount)

        context['data'] = zip(context['prfdetailtemp'], context['amount'])

        return context

    def form_valid(self, form):
        if Prfdetailtemp.objects.filter(Q(isdeleted=0), Q(prfmain=self.object.pk) | Q(secretkey=self.request.POST['secretkey'])):
            self.object = form.save(commit=False)
            self.object.branch = Branch.objects.get(pk=5)  # head office

            self.object.modifyby = self.request.user
            self.object.modifydate = datetime.datetime.now()

            if self.object.prfstatus == 'A':
                self.object.save(update_fields=['particulars', 'modifyby', 'modifydate'])
            else:
                self.object.save(update_fields=['prfdate', 'inventoryitemtype', 'prftype', 'urgencytype',
                                            'dateneeded', 'branch', 'particulars', 'designatedapprover',
                                            'modifyby', 'modifydate'])

                Prfdetailtemp.objects.filter(isdeleted=1, prfmain=self.object.pk).delete()

                detailtagasdeleted = Prfdetail.objects.filter(prfmain=self.object.pk)
                for dtd in detailtagasdeleted:
                    dtd.isdeleted = 1
                    dtd.save()

                alltempdetail = Prfdetailtemp.objects.filter(
                    Q(isdeleted=0),
                    Q(prfmain=self.object.pk) | Q(secretkey=self.request.POST['secretkey'])
                ).order_by('enterdate')

                # remove old detail in rfquantities
                prfdetail = Prfdetail.objects.filter(prfmain=self.object.id, isdeleted=1)
                for data in prfdetail:
                    if Rfprftransaction.objects.filter(prfdetail=data.id):
                        deleteRfprftransactionitem(data)
                Prfdetail.objects.filter(prfmain=self.object.pk, isdeleted=1).delete()

                itemquantity = 0
                prfmain = Prfmain.objects.get(pk=self.object.pk)
                i = 1
                for atd in alltempdetail:

                    department = Department.objects.get(pk=self.request.POST.getlist('temp_department')[i-1], isdeleted=0)

                    alldetail = Prfdetail()
                    alldetail.item_counter = i
                    alldetail.prfmain = Prfmain.objects.get(prfnum=self.request.POST['prfnum'])
                    alldetail.invitem = atd.invitem
                    alldetail.invitem_code = atd.invitem_code
                    alldetail.invitem_name = atd.invitem_name
                    alldetail.invitem_unitofmeasure = Unitofmeasure.objects.get(code=self.request.POST.getlist('temp_item_um')[i-1], isdeleted=0, status='A')
                    alldetail.invitem_unitofmeasure_code = Unitofmeasure.objects.get(code=self.request.POST.getlist('temp_item_um')[i-1], isdeleted=0, status='A').code
                    alldetail.quantity = self.request.POST.getlist('temp_quantity')[i-1]
                    alldetail.department = Department.objects.get(pk=self.request.POST.getlist('temp_department')[i-1])
                    alldetail.department_code = department.code
                    alldetail.department_name = department.departmentname
                    alldetail.remarks = self.request.POST.getlist('temp_remarks')[i-1]
                    alldetail.currency = Currency.objects.get(pk=self.request.POST.getlist('temp_item_currency')[i-1])
                    alldetail.fxrate = self.request.POST.getlist('temp_fxrate')[i-1]
                    alldetail.status = atd.status
                    alldetail.enterby = atd.enterby
                    alldetail.enterdate = atd.enterdate
                    alldetail.modifyby = atd.modifyby
                    alldetail.modifydate = atd.modifydate
                    alldetail.postby = atd.postby
                    alldetail.postdate = atd.postdate
                    alldetail.isdeleted = atd.isdeleted
                    alldetail.rfmain = atd.rfmain
                    alldetail.rfdetail = atd.rfdetail
                    alldetail.poremainingquantity = self.request.POST.getlist('temp_quantity')[i-1]
                    alldetail.save()
                    atd.delete()

                    if atd.rfmain:
                        if addRfprftransactionitem(alldetail.id):
                            itemquantity = int(itemquantity) + int(alldetail.quantity)
                        else:
                            alldetail.delete()
                    else:
                        itemquantity = int(itemquantity) + int(alldetail.quantity)


                    i += 1

                prfmain.quantity = int(itemquantity)
                prfmain.totalquantity = int(itemquantity)
                prfmain.totalremainingquantity = int(itemquantity)
                prfmain.save()

            Prfdetailtemp.objects.filter(prfmain=self.object.pk).delete()

            return HttpResponseRedirect('/purchaserequisitionform/' + str(self.object.id) + '/update/')


@method_decorator(login_required, name='dispatch')
class DeleteView(DeleteView):
    model = Prfmain
    template_name = 'purchaserequisitionform/delete.html'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.has_perm('purchaserequisitionform.delete_prfmain') or \
                        self.object.status == 'O' or \
                        self.object.prfstatus == 'A':
            raise Http404
        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.modifyby = self.request.user
        self.object.modifydate = datetime.datetime.now()
        self.object.isdeleted = 1
        self.object.status = 'C'
        self.object.prfstatus = 'D'
        self.object.save()

        prfdetail = Prfdetail.objects.filter(prfmain=self.object.id)
        for data in prfdetail:
            deleteRfprftransactionitem(data)

        return HttpResponseRedirect('/purchaserequisitionform')


@method_decorator(login_required, name='dispatch')
class Pdf(PDFTemplateView):
    model = Prfmain
    template_name = 'purchaserequisitionform/pdf.html'

    def get_context_data(self, **kwargs):
        context = super(Pdf, self).get_context_data(**kwargs)
        context['prfmain'] = Prfmain.objects.get(pk=self.kwargs['pk'], isdeleted=0, status='A')
        context['prfdetail'] = Prfdetail.objects.filter(prfmain=self.kwargs['pk'], isdeleted=0, status='A').order_by('item_counter')

        printedprf = Prfmain.objects.get(pk=self.kwargs['pk'], isdeleted=0, status='A')
        printedprf.print_ctr += 1
        printedprf.save()

        return context


@csrf_exempt
def importItems(request):
    if request.method == 'POST':
        rfdetail = Rfdetail.objects\
                        .raw('SELECT inv.unitcost, '
                                    'inv.id AS inv_id, '
                                    'rfm.rfnum, '
                                    'rfm.department_id, '
                                    'rfm.id AS rfm_id, '
                                    'rfd.invitem_code, '
                                    'rfd.invitem_name, '
                                    'rfd.quantity, '
                                    'rfd.remarks, '
                                    'rfd.invitem_unitofmeasure_id AS um_id, '
                                    'rfd.invitem_unitofmeasure_code AS um_code, '
                                    'rfd.id, '
                                    'rfd.isfullyprf, '
                                    'rfd.prfremainingquantity, '
                                    'um.code '
                            'FROM rfmain rfm '
                            'LEFT JOIN rfdetail rfd '
                            'ON rfd.rfmain_id = rfm.id '
                            'LEFT JOIN inventoryitem inv '
                            'ON inv.id = rfd.invitem_id '
                            'LEFT JOIN unitofmeasure um '
                            'ON um.id = inv.unitofmeasure_id '
                            'WHERE '
                                'rfd.rfmain_id = ' + request.POST['rfnum'] + ' AND '
                                'rfm.rfstatus = "A" AND '
                                'rfm.status = "A" AND '
                                'rfm.isdeleted = 0 AND '
                                'rfd.status = "A" AND '
                                'rfd.isdeleted = 0 AND '
                                'inv.status = "A"'
                            'ORDER BY rfd.item_counter')

        prfdata = []

        item_counter = int(request.POST['itemno'])

        for data in rfdetail:
            if data.isfullyprf != 1 and data.prfremainingquantity > 0:
                prfdata.append([data.invitem_code,
                                data.invitem_name,
                                data.code,
                                data.rfnum,
                                data.remarks,
                                data.quantity,
                                data.unitcost,
                                data.id,
                                item_counter,
                                data.um_code,
                                data.prfremainingquantity,
                                data.department_id])

                department = Department.objects.get(pk=data.department_id, isdeleted=0)

                detailtemp = Prfdetailtemp()
                detailtemp.invitem_code = data.invitem_code
                detailtemp.invitem_name = data.invitem_name
                detailtemp.invitem_unitofmeasure = Unitofmeasure.objects.get(pk=data.um_id)
                detailtemp.invitem_unitofmeasure_code = data.um_code
                detailtemp.item_counter = item_counter
                detailtemp.quantity = data.quantity
                detailtemp.department_code = department.code
                detailtemp.department_name = department.departmentname
                detailtemp.department = Department.objects.get(pk=data.department_id)
                detailtemp.remarks = data.remarks
                detailtemp.currency = Currency.objects.get(pk=1)
                detailtemp.status = 'A'
                detailtemp.enterdate = datetime.datetime.now()
                detailtemp.modifydate = datetime.datetime.now()
                detailtemp.enterby = request.user
                detailtemp.modifyby = request.user
                detailtemp.secretkey = request.POST['secretkey']
                detailtemp.invitem = Inventoryitem.objects.get(pk=data.inv_id)
                detailtemp.rfmain = Rfmain.objects.get(pk=data.rfm_id)
                detailtemp.rfdetail = Rfdetail.objects.get(pk=data.id)
                detailtemp.save()

                item_counter += 1

        data = {
            'status': 'success',
            'prfdata': prfdata,
        }
    else:
        data = {
            'status': 'error',
        }

    return JsonResponse(data)


@csrf_exempt
def savedetailtemp(request):
    if request.method == 'POST':
        invdetail = Inventoryitem.objects\
                        .raw('SELECT inv.unitcost, '
                                    'inv.code, '
                                    'inv.description, '
                                    'inv.id, '
                                    'um.code AS um_code '
                            'FROM inventoryitem inv '
                            'LEFT JOIN unitofmeasure um '
                            'ON um.id = inv.unitofmeasure_id '
                            'WHERE '
                                'inv.status = "A" AND '
                                'inv.id = ' + request.POST['inv_id'])

        for data in invdetail:
            prfdata = [data.code,
                       data.description,
                       data.um_code,
                       data.unitcost,
                       data.id]

            department = Department.objects.get(pk=request.POST['department'], isdeleted=0)

            detailtemp = Prfdetailtemp()
            detailtemp.invitem_code = data.code
            detailtemp.invitem_name = data.description
            detailtemp.item_counter = request.POST['itemno']
            detailtemp.quantity = request.POST['quantity']
            detailtemp.department_code = department.code
            detailtemp.department_name = department.departmentname
            detailtemp.department = Department.objects.get(pk=request.POST['department'])
            detailtemp.remarks = request.POST['remarks']
            detailtemp.invitem_unitofmeasure = Inventoryitem.objects.get(pk=request.POST['inv_id']).unitofmeasure
            detailtemp.invitem_unitofmeasure_code = Inventoryitem.objects.get(pk=request.POST['inv_id']).unitofmeasure.code
            detailtemp.currency = Currency.objects.get(pk=request.POST['currency'], isdeleted=0, status='A')
            detailtemp.status = 'A'
            detailtemp.enterdate = datetime.datetime.now()
            detailtemp.modifydate = datetime.datetime.now()
            detailtemp.enterby = request.user
            detailtemp.modifyby = request.user
            detailtemp.secretkey = request.POST['secretkey']
            detailtemp.invitem = Inventoryitem.objects.get(pk=request.POST['inv_id'], status='A')
            detailtemp.save()

        data = {
            'status': 'success',
            'prfdata': prfdata,
            'remarks': request.POST['remarks'],
            'currency': Currency.objects.get(pk=request.POST['currency']).symbol,
            'itemno': request.POST['itemno'],
        }
    else:
        data = {
            'status': 'error',
        }

    return JsonResponse(data)


@csrf_exempt
def deletedetailtemp(request):

    if request.method == 'POST':
        try:
            detailtemp = Prfdetailtemp.objects.get(item_counter=request.POST['itemno'], secretkey=request.POST['secretkey'], prfmain=None)
            detailtemp.delete()
        except Prfdetailtemp.DoesNotExist:
            detailtemp = Prfdetailtemp.objects.get(item_counter=request.POST['itemno'], prfmain__prfnum=request.POST['prfnum'])
            detailtemp.isdeleted = 1
            detailtemp.save()

        data = {
            'status': 'success',
        }
    else:
        data = {
            'status': 'error',
        }

    return JsonResponse(data)


def updateTransaction(pk, status):
    csdata = Csdata.objects.get(prfmain=pk, isdeleted=0)
    if csdata and Csmain.objects.get(pk=csdata.csmain.pk, status='A', isdeleted=0):

        if status == 'A':

            prfdetail = Prfdetail.objects.filter(prfmain=pk, isdeleted=0)

            for data in prfdetail:
                csdetail = Csdetail.objects.filter(csmain=csdata.csmain.pk,
                                                csstatus=1,
                                                prfdetail=data.pk,
                                                status='A',
                                                isdeleted=0).first()

                if csdetail:
                    data.negocost = csdetail.negocost
                    data.vatable = csdetail.vatable
                    data.vatexempt = csdetail.vatexempt
                    data.vatzerorated = csdetail.vatzerorated
                    data.grosscost = csdetail.grosscost
                    data.grossamount = csdetail.grossamount
                    data.vatamount = csdetail.vatamount
                    data.netamount = csdetail.netamount
                    data.uc_cost = csdetail.unitcost
                    data.uc_vatable = csdetail.uc_vatable
                    data.uc_vatexempt = csdetail.uc_vatexempt
                    data.uc_vatzerorated = csdetail.uc_vatzerorated
                    data.uc_grosscost = csdetail.uc_grosscost
                    data.uc_grossamount = csdetail.uc_grossamount
                    data.uc_vatamount = csdetail.uc_vatamount
                    data.uc_netamount = csdetail.uc_netamount

                    data.csmain = Csmain.objects.get(pk=csdata.csmain.pk).pk
                    data.csdetail = Csdetail.objects.get(pk=csdetail.pk).pk
                    data.csnum = csdata.csmain.csnum
                    data.csdate = csdata.csmain.csdate

                    data.supplier = Supplier.objects.get(pk=csdetail.supplier.pk)
                    data.suppliercode = csdetail.supplier.code
                    data.suppliername = csdetail.supplier.name
                    data.estimateddateofdelivery = csdetail.estimateddateofdelivery
                    data.save()

            data = Csdetail.objects.filter(csmain=csdata.csmain.pk,
                                           csstatus=1,
                                           prfmain=pk,
                                           status='A',
                                           isdeleted=0).aggregate(Sum('negocost'),
                                                                  Sum('vatable'),
                                                                  Sum('vatexempt'),
                                                                  Sum('vatzerorated'),
                                                                  Sum('grosscost'),
                                                                  Sum('grossamount'),
                                                                  Sum('vatamount'),
                                                                  Sum('netamount'),
                                                                  Sum('unitcost'),
                                                                  Sum('uc_vatable'),
                                                                  Sum('uc_vatexempt'),
                                                                  Sum('uc_vatzerorated'),
                                                                  Sum('uc_grosscost'),
                                                                  Sum('uc_grossamount'),
                                                                  Sum('uc_vatamount'),
                                                                  Sum('uc_netamount'))
            Prfmain.objects.filter(pk=pk,
                                   prfstatus='A',
                                   isdeleted=0).update(negocost=data['negocost__sum'],
                                                       vatable=data['vatable__sum'],
                                                       vatexempt=data['vatexempt__sum'],
                                                       vatzerorated=data['vatzerorated__sum'],
                                                       grosscost=data['grosscost__sum'],
                                                       grossamount=data['grossamount__sum'],
                                                       vatamount=data['vatamount__sum'],
                                                       netamount=data['netamount__sum'],
                                                       uc_cost=data['unitcost__sum'],
                                                       uc_vatable=data['uc_vatable__sum'],
                                                       uc_vatexempt=data['uc_vatexempt__sum'],
                                                       uc_vatzerorated=data['uc_vatzerorated__sum'],
                                                       uc_grosscost=data['uc_grosscost__sum'],
                                                       uc_grossamount=data['uc_grossamount__sum'],
                                                       uc_vatamount=data['uc_vatamount__sum'],
                                                       uc_netamount=data['uc_netamount__sum'])

        elif status == 'D':

            prfdetail = Prfdetail.objects.filter(prfmain=pk, isdeleted=0)

            for data in prfdetail:
                csdetail = Csdetail.objects.filter(csmain=csdata.csmain.pk,
                                                csstatus=1,
                                                prfdetail=data.pk,
                                                status='A',
                                                isdeleted=0).first()

                if csdetail:

                    data.negocost = 0
                    data.vatable = 0
                    data.vatexempt = 0
                    data.vatzerorated = 0
                    data.grosscost = 0
                    data.grossamount = 0
                    data.vatamount = 0
                    data.netamount = 0
                    data.uc_cost = 0
                    data.uc_vatable = 0
                    data.uc_vatexempt = 0
                    data.uc_vatzerorated = 0
                    data.uc_grosscost = 0
                    data.uc_grossamount = 0
                    data.uc_vatamount = 0
                    data.uc_netamount = 0

                    data.csmain = None
                    data.csdetail = None
                    data.csnum = None
                    data.csdate = None

                    data.supplier = None
                    data.suppliercode = None
                    data.suppliername = None
                    data.estimateddateofdelivery = None
                    data.save()

            Prfmain.objects.filter(pk=pk,
                                   prfstatus='A',
                                   isdeleted=0).update(vatable=0, vatexempt=0, vatzerorated=0, grosscost=0,
                                                       grossamount=0, vatamount=0, netamount=0, uc_vatable=0,
                                                       uc_vatexempt=0, uc_vatzerorated=0, uc_grosscost=0,
                                                       uc_grossamount=0, uc_vatamount=0, uc_netamount=0)


def comments():
    print 123
    # handle cs getting vat total with different currency
    # update import select behind modal
    # quantity cost front end change
    # delete item prompt
    # delete prfmain prompt
    # handle bloating in prfdetailtemp