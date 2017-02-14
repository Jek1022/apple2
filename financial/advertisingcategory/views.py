from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, Http404
from advertisingcategory.models import Advertisingcategory
import datetime


@method_decorator(login_required, name='dispatch')
class IndexView(ListView):
    model = Advertisingcategory
    template_name = 'advertisingcategory/index.html'
    context_object_name = 'data_list'

    def get_queryset(self):
        return Advertisingcategory.objects.all().filter(isdeleted=0).order_by('-pk')


@method_decorator(login_required, name='dispatch')
class DetailView(DetailView):
    model = Advertisingcategory
    template_name = 'advertisingcategory/detail.html'


@method_decorator(login_required, name='dispatch')
class CreateView(CreateView):
    model = Advertisingcategory
    template_name = 'advertisingcategory/create.html'
    fields = ['code', 'description']

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('advertisingcategory.add_advertisingcategory'):
            raise Http404
        return super(CreateView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.enterby = self.request.user
        self.object.modifyby = self.request.user
        self.object.save()
        return HttpResponseRedirect('/advertisingcategory')


@method_decorator(login_required, name='dispatch')
class UpdateView(UpdateView):
    model = Advertisingcategory
    template_name = 'advertisingcategory/edit.html'
    fields = ['code', 'description']

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('advertisingcategory.change_advertisingcategory'):
            raise Http404
        return super(UpdateView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.modifyby = self.request.user
        self.object.modifydate = datetime.datetime.now()
        self.object.save(update_fields=['description', 'modifyby', 'modifydate'])
        return HttpResponseRedirect('/advertisingcategory')


@method_decorator(login_required, name='dispatch')
class DeleteView(DeleteView):
    model = Advertisingcategory
    template_name = 'advertisingcategory/delete.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('advertisingcategory.delete_advertisingcategory'):
            raise Http404
        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.modifyby = self.request.user
        self.object.modifydate = datetime.datetime.now()
        self.object.isdeleted = 1
        self.object.status = 'I'
        self.object.save()
        return HttpResponseRedirect('/advertisingcategory')
