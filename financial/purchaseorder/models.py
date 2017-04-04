from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User
import datetime


class Pomain(models.Model):
    ponum = models.CharField(max_length=10, unique=True)
    podate = models.DateField()
    refnum = models.CharField(max_length=150, null=True, blank=True)
    potype = models.CharField(max_length=150, default='REGULAR')
    URGENCY_CHOICES = (
        ('N', 'Normal'),
        ('R', 'Rush'),
    )
    urgencytype = models.CharField(max_length=1, choices=URGENCY_CHOICES, default='N')
    dateneeded = models.DateField()
    particulars = models.TextField()
    PO_STATUS_CHOICES = (
        ('F', 'For Approval'),
        ('A', 'Approved'),
        ('D', 'Disapproved'),
    )
    postatus = models.CharField(max_length=1, choices=PO_STATUS_CHOICES, default='A')     # not present in CREATE screen
    remarks = models.CharField(max_length=250, null=True, blank=True)                     # not present in CREATE screen
    supplier = models.ForeignKey('supplier.Supplier', related_name='pomain_supplier_id')
    supplier_code = models.CharField(max_length=25)
    supplier_name = models.CharField(max_length=250)
    apnum = models.CharField(max_length=150, null=True, blank=True)
    apdate = models.DateField(null=True, blank=True)
    ataxcode = models.ForeignKey('ataxcode.Ataxcode', related_name='pomain_ataxcode_id', null=True, blank=True)
    inputvat = models.ForeignKey('inputvat.Inputvat', related_name='pomain_inputvat_id', null=True, blank=True)
    vat = models.ForeignKey('vat.Vat', related_name='pomain_vat_id')
    creditterm = models.ForeignKey('creditterm.Creditterm', related_name='pomain_creditterm_id', null=True, blank=True)
    STATUS_CHOICES = (
        ('A', 'Active'),
        ('I', 'Inactive'),
        ('C', 'Cancelled'),
        ('O', 'Posted'),
        ('P', 'Printed'),
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    enterby = models.ForeignKey(User, default=1, related_name='pomain_enter')
    enterdate = models.DateTimeField(auto_now_add=True)
    modifyby = models.ForeignKey(User, default=1, related_name='pomain_modify')
    modifydate = models.DateTimeField(default=datetime.datetime.now())
    postby = models.ForeignKey(User, related_name='pomain_post', null=True, blank=True)
    postdate = models.DateTimeField(null=True, blank=True)
    isdeleted = models.IntegerField(default=0)

    class Meta:
        db_table = 'pomain'
        ordering = ['-pk']
        # permissions = (("view_requisitionform", "Can view requisitionform"),)

    def get_absolute_url(self):
        return reverse('purchaseorder:detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.ponum

    def __unicode__(self):
        return self.ponum


class Podetail(models.Model):
    pomain = models.ForeignKey('purchaseorder.Pomain', related_name='podetail_pomain_id', null=True, blank=True)
    item_counter = models.IntegerField()
    invitem = models.ForeignKey('inventoryitem.Inventoryitem', related_name='podetail_invitem_id')
    invitem_code = models.CharField(max_length=25)
    invitem_name = models.CharField(max_length=250)
    invitem_unitofmeasure = models.CharField(max_length=50)
    quantity = models.IntegerField(default=0)
    unitcost = models.FloatField(default=0.00)
    branch = models.ForeignKey('branch.Branch', related_name='podetail_branch_id')
    department = models.ForeignKey('department.Department', related_name='podetail_department_id', blank=True,
                                   null=True)
    discountrate = models.IntegerField(default=0, null=True, blank=True)
    remarks = models.CharField(max_length=250, null=True, blank=True)
    STATUS_CHOICES = (
        ('A', 'Active'),
        ('I', 'Inactive'),
        ('C', 'Cancelled'),
        ('O', 'Posted'),
        ('P', 'Printed'),
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    enterby = models.ForeignKey(User, default=1, related_name='podetail_enter')
    enterdate = models.DateTimeField(default=datetime.datetime.now())
    modifyby = models.ForeignKey(User, default=1, related_name='podetail_modify')
    modifydate = models.DateTimeField(default=datetime.datetime.now())
    postby = models.ForeignKey(User, related_name='podetail_post', null=True, blank=True)
    postdate = models.DateTimeField(null=True, blank=True)
    isdeleted = models.IntegerField(default=0)

    class Meta:
        db_table = 'podetail'
        ordering = ['-pk']

    def get_absolute_url(self):
        return reverse('purchaseorder:detail', kwargs={'pk': self.pk})

    def __str__(self):
        return str(self.pk) + ' ' + str(self.item_counter) + ' ' + self.invitem_name

    def __unicode__(self):
        return str(self.pk) + ' ' + str(self.item_counter) + ' ' + self.invitem_name


class Podetailtemp(models.Model):
    pomain = models.ForeignKey('purchaseorder.Pomain', related_name='podetailtemp_pomain_id', null=True, blank=True)
    podetail = models.ForeignKey('purchaseorder.Podetail', related_name='podetailtemp_podetail_id', null=True,
                                 blank=True)
    item_counter = models.IntegerField()
    invitem = models.ForeignKey('inventoryitem.Inventoryitem', related_name='podetailtemp_invitem_id')
    invitem_code = models.CharField(max_length=25)
    invitem_name = models.CharField(max_length=250)
    invitem_unitofmeasure = models.CharField(max_length=50)
    quantity = models.IntegerField(default=0)
    unitcost = models.FloatField(default=0.00)
    branch = models.ForeignKey('branch.Branch', related_name='podetailtemp_branch_id')
    department = models.ForeignKey('department.Department', related_name='podetailtemp_department_id', blank=True,
                                   null=True)
    discountrate = models.IntegerField(default=0, null=True, blank=True)
    remarks = models.CharField(max_length=250, null=True, blank=True)
    STATUS_CHOICES = (
        ('A', 'Active'),
        ('I', 'Inactive'),
        ('C', 'Cancelled'),
        ('O', 'Posted'),
        ('P', 'Printed'),
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    enterby = models.ForeignKey(User, default=1, related_name='podetailtemp_enter')
    enterdate = models.DateTimeField(default=datetime.datetime.now())
    modifyby = models.ForeignKey(User, default=1, related_name='podetailtemp_modify')
    modifydate = models.DateTimeField(default=datetime.datetime.now())
    postby = models.ForeignKey(User, related_name='podetailtemp_post', null=True, blank=True)
    postdate = models.DateTimeField(null=True, blank=True)
    isdeleted = models.IntegerField(default=0)
    secretkey = models.CharField(max_length=255)

    class Meta:
        db_table = 'podetailtemp'
        ordering = ['-pk']

    def get_absolute_url(self):
        return reverse('purchaseorder:detail', kwargs={'pk': self.pk})

    def __str__(self):
        return str(self.pk) + ' ' + str(self.item_counter) + ' ' + self.invitem_name + ' temp'

    def __unicode__(self):
        return str(self.pk) + ' ' + str(self.item_counter) + ' ' + self.invitem_name + ' temp'
