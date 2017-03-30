from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from . models import Prfmain
from requisitionform.models import Rfmain, Rfdetail
from purchaserequisitionform.models import Prfmain, Prfdetail, Prfdetailtemp
from inventoryitemtype.models import Inventoryitemtype
from inventoryitem.models import Inventoryitem
from branch.models import Branch
from department.models import Department
from django.contrib.auth.models import User
from django.db.models import Q
from acctentry.views import generatekey
from easy_pdf.views import PDFTemplateView
import datetime


@method_decorator(login_required, name='dispatch')
class IndexView(ListView):
    model = Prfmain
    template_name = 'purchaserequisitionform/index.html'
    context_object_name = 'data_list'

    def get_queryset(self):
        return Prfmain.objects.all().filter(isdeleted=0, prfstatus='F').order_by('enterdate')


@method_decorator(login_required, name='dispatch')
class DetailView(DetailView):
    model = Prfmain
    template_name = 'purchaserequisitionform/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['prfdetail'] = Prfdetail.objects.filter(isdeleted=0).filter(prfmain=self.kwargs['pk']).\
            order_by('item_counter')
        return context


@method_decorator(login_required, name='dispatch')
class CreateView(CreateView):
    model = Prfmain
    template_name = 'purchaserequisitionform/create.html'
    fields = ['prfdate', 'inventoryitemtype', 'designatedapprover', 'prftype', 'particulars', 'department', 'branch', 'urgencytype', 'dateneeded']

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['secretkey'] = generatekey(self)
        context['inventoryitemtype'] = Inventoryitemtype.objects.filter(isdeleted=0)
        context['branch'] = Branch.objects.filter(isdeleted=0, code='HO')
        context['department'] = Department.objects.filter(isdeleted=0).order_by('departmentname')
        context['invitem'] = Inventoryitem.objects.filter(isdeleted=0).order_by('inventoryitemclass__inventoryitemtype__code', 'description')
        context['rfmain'] = Rfmain.objects.filter(isdeleted=0, rfstatus='A', status='A')
        context['designatedapprover'] = User.objects.filter(is_active=1).exclude(username='admin').order_by('first_name')
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)

        try:
            prfnumlast = Prfmain.objects.latest('prfnum')
            latestprfnum = str(prfnumlast)
            if latestprfnum[0:4] == str(datetime.datetime.now().year):
                prfnum = str(datetime.datetime.now().year)
                last = str(int(latestprfnum[4:])+1)
                zero_addon = 6 - len(last)
                for x in range(0, zero_addon):
                    prfnum += '0'
                prfnum += last
            else:
                prfnum = str(datetime.datetime.now().year) + '000001'
        except Prfmain.DoesNotExist:
            prfnum = str(datetime.datetime.now().year) + '000001'

        self.object.prfnum = prfnum

        self.object.enterby = self.request.user
        self.object.modifyby = self.request.user
        self.object.save()

        detailtemp = Prfdetailtemp.objects.filter(isdeleted=0, secretkey=self.request.POST['secretkey']).\
            order_by('enterdate')
        i = 1
        for dt in detailtemp:
            detail = Prfdetail()
            detail.item_counter = i
            detail.prfmain = Prfmain.objects.get(prfnum=prfnum)
            detail.invitem_code = dt.invitem_code
            detail.invitem_name = dt.invitem_name
            detail.quantity = self.request.POST.getlist('temp_quantity')[i-1]
            detail.status = dt.status
            detail.enterby = dt.enterby
            detail.enterdate = dt.enterdate
            detail.modifyby = dt.modifyby
            detail.modifydate = dt.modifydate
            detail.postby = dt.postby
            detail.postdate = dt.postdate
            detail.isdeleted = dt.isdeleted
            detail.invitem = dt.invitem
            detail.rfdetail = dt.rfdetail
            detail.save()
            dt.delete()
            i += 1

        return HttpResponseRedirect('/purchaserequisitionform/' + str(self.object.id))


class UpdateView(UpdateView):
    model = Prfmain
    template_name = 'purchaserequisitionform/edit.html'
    fields = ['prfnum', 'prfdate', 'inventoryitemtype', 'designatedapprover', 'prftype', 'particulars', 'department', 'branch', 'urgencytype', 'dateneeded']

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['secretkey'] = generatekey(self)
        context['inventoryitemtype'] = Inventoryitemtype.objects.filter(isdeleted=0)
        context['branch'] = Branch.objects.filter(isdeleted=0, code='HO')
        context['department'] = Department.objects.filter(isdeleted=0).order_by('departmentname')
        context['invitem'] = Inventoryitem.objects.filter(isdeleted=0).order_by('inventoryitemclass__inventoryitemtype__code', 'description')
        context['rfmain'] = Rfmain.objects.filter(isdeleted=0, rfstatus='A', status='A')
        context['designatedapprover'] = User.objects.filter(is_active=1).exclude(username='admin').order_by('first_name')

        Prfdetailtemp.objects.filter(prfmain=self.object.pk).delete()        # clear all temp data

        detail = Prfdetail.objects.filter(isdeleted=0, prfmain=self.object.pk).order_by('item_counter')
        for d in detail:
            detailtemp = Prfdetailtemp()
            detailtemp.invitem_code = d.invitem_code
            detailtemp.invitem_name = d.invitem_name
            detailtemp.item_counter = d.item_counter
            detailtemp.quantity = d.quantity
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
            detailtemp.rfdetail = d.rfdetail
            detailtemp.save()

        context['prfdetailtemp'] = Prfdetailtemp.objects.filter(isdeleted=0, prfmain=self.object.pk).order_by('item_counter')
        context['amount'] = []

        for data in context['prfdetailtemp']:
            amount = float(data.quantity) * float(data.invitem.unitcost)
            context['amount'].append(amount)

        context['data'] = zip(context['prfdetailtemp'], context['amount'])

        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.modifyby = self.request.user
        self.object.modifydate = datetime.datetime.now()
        self.object.save(update_fields=['prfdate', 'inventoryitemtype', 'prftype', 'urgencytype',
                                        'dateneeded', 'branch', 'department', 'particulars', 'designatedapprover',
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

        print "----------------------"
        print alltempdetail
        print "----------------------"

        i = 1
        for atd in alltempdetail:
            alldetail = Prfdetail()
            alldetail.item_counter = i
            alldetail.prfmain = Prfmain.objects.get(prfnum=self.request.POST['prfnum'])
            alldetail.invitem = atd.invitem
            alldetail.invitem_code = atd.invitem_code
            alldetail.invitem_name = atd.invitem_name
            alldetail.quantity = self.request.POST.getlist('temp_quantity')[i-1]
            alldetail.status = atd.status
            alldetail.enterby = atd.enterby
            alldetail.enterdate = atd.enterdate
            alldetail.modifyby = atd.modifyby
            alldetail.modifydate = atd.modifydate
            alldetail.postby = atd.postby
            alldetail.postdate = atd.postdate
            alldetail.isdeleted = atd.isdeleted
            alldetail.rfdetail = atd.rfdetail
            alldetail.save()
            atd.delete()
            i += 1

        Prfdetailtemp.objects.filter(prfmain=self.object.pk).delete()
        Prfdetail.objects.filter(prfmain=self.object.pk, isdeleted=1).delete()

        return HttpResponseRedirect('/purchaserequisitionform/')


@method_decorator(login_required, name='dispatch')
class DeleteView(DeleteView):
    model = Prfmain
    template_name = 'purchaserequisitionform/delete.html'

    def dispatch(self, request, *args, **kwargs):
        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.modifyby = self.request.user
        self.object.modifydate = datetime.datetime.now()
        self.object.isdeleted = 1
        self.object.status = 'I'
        self.object.save()
        return HttpResponseRedirect('/purchaserequisitionform')


@method_decorator(login_required, name='dispatch')
class Pdf(PDFTemplateView):
    model = Prfmain
    template_name = 'purchaserequisitionform/pdf.html'

    def get_context_data(self, **kwargs):
        context = super(Pdf, self).get_context_data(**kwargs)
        context['prfmain'] = Prfmain.objects.get(pk=self.kwargs['pk'], isdeleted=0, status='A', prfstatus='F')
        context['prfdetail'] = Prfdetail.objects.filter(prfmain=self.kwargs['pk'], isdeleted=0, status='A').order_by('item_counter')
        return context


@csrf_exempt
def importItems(request):
    # validation on save
    # item no / counter validation..
    # quantity cost front end change

    if request.method == 'POST':
        rfdetail = Rfdetail.objects\
                        .raw('SELECT inv.unitcost, '
                                    'inv.id AS inv_id, '
                                    'rfm.rfnum, '
                                    'rfd.invitem_code, '
                                    'rfd.invitem_name, '
                                    'rfd.quantity, '
                                    'rfd.remarks, '
                                    'rfd.id, '
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
            prfdata.append([data.invitem_code,
                            data.invitem_name,
                            data.code,
                            data.rfnum,
                            data.remarks,
                            data.quantity,
                            data.unitcost,
                            data.id,
                            item_counter])

            detailtemp = Prfdetailtemp()
            detailtemp.invitem_code = data.invitem_code
            detailtemp.invitem_name = data.invitem_name
            detailtemp.item_counter = item_counter
            detailtemp.quantity = data.quantity
            detailtemp.status = 'A'
            detailtemp.enterdate = datetime.datetime.now()
            detailtemp.modifydate = datetime.datetime.now()
            detailtemp.enterby = request.user
            detailtemp.modifyby = request.user
            detailtemp.secretkey = request.POST['secretkey']
            detailtemp.invitem = Inventoryitem.objects.get(pk=data.inv_id)
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

            detailtemp = Prfdetailtemp()
            detailtemp.invitem_code = data.code
            detailtemp.invitem_name = data.description
            detailtemp.item_counter = request.POST['itemno']
            detailtemp.quantity = request.POST['quantity']
            detailtemp.status = 'A'
            detailtemp.enterdate = datetime.datetime.now()
            detailtemp.modifydate = datetime.datetime.now()
            detailtemp.enterby = request.user
            detailtemp.modifyby = request.user
            detailtemp.secretkey = request.POST['secretkey']
            detailtemp.invitem = Inventoryitem.objects.get(pk=request.POST['inv_id'])
            detailtemp.save()

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
def deletedetailtemp(request):

    if request.method == 'POST':
        print request.POST
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

