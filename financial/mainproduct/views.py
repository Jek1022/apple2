import datetime
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, Http404
from mainproduct.models import Mainproduct
from financial.utils import Render
from django.utils import timezone
from django.template.loader import get_template
from django.http import HttpResponse
from companyparameter.models import Companyparameter

#import pprint

# Create your views here.
@method_decorator(login_required, name='dispatch')
class IndexView(ListView):
    model = Mainproduct
    template_name = 'mainproduct/index.html'
    context_object_name = 'data_list'

    def get_queryset(self):
        return Mainproduct.objects.all().filter(isdeleted=0).order_by('-pk')

@method_decorator(login_required, name='dispatch')
class DetailView(DetailView):
    model = Mainproduct
    template_name = 'mainproduct/detail.html'

@method_decorator(login_required, name='dispatch')
class CreateView(CreateView):
    model = Mainproduct
    template_name = 'mainproduct/create.html'
    fields = ['code', 'description']

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('mainproduct.add_mainproduct'):
            raise Http404
        return super(CreateView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.enterby = self.request.user
        self.object.modifyby = self.request.user
        self.object.save()
        return HttpResponseRedirect('/mainproduct')

@method_decorator(login_required, name='dispatch')
class UpdateView(UpdateView):
    model = Mainproduct
    template_name = 'mainproduct/edit.html'
    fields = ['code', 'description']

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('mainproduct.change_mainproduct'):
            raise Http404
        return super(UpdateView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.modifyby = self.request.user
        self.object.modifydate = datetime.datetime.now()
        self.object.save(update_fields=['description', 'modifyby', 'modifydate'])
        return HttpResponseRedirect('/mainproduct')

@method_decorator(login_required, name='dispatch')
class DeleteView(DeleteView):
    model = Mainproduct
    template_name = 'mainproduct/delete.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('mainproduct.delete_mainproduct'):
            raise Http404
        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.modifyby = self.request.user
        self.object.modifydate = datetime.datetime.now()
        self.object.isdeleted = 1
        self.object.status = 'I'
        self.object.save()
        return HttpResponseRedirect('/mainproduct')

@method_decorator(login_required, name='dispatch')
class GeneratePDF(View):
    def get(self, request):
        company = Companyparameter.objects.all().first()
        list = Mainproduct.objects.filter(isdeleted=0).order_by('code')
        context = {
            "title": "Main Product Master List",
            "today": timezone.now(),
            "company": company,
            "list": list,
            "username": request.user,
        }
        return Render.render('mainproduct/list.html', context)