from django.contrib import admin
from .models import *

# xprf inso cuib tvai -- app password *

# Register your models here.
class UserDisplay(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False
    readonly_fields = ['name','email','password']
    list_display = ['email','name','role','company','department']

class RoleDisplay(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False

class TicketDisplay(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False
    readonly_fields = ['ticket_id','title','category','requestor','created_at','company','department','required_by','description','justification','estimated_delivery','total_estimated_cost','comment']
    list_display = ("ticket_id","requestor","status","total_estimated_cost")

class TicketItemDisplay(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False
    readonly_fields = ['ticket_id','name','budget','quantity','unit']
    list_display = ("ticket_id","name","budget","quantity","unit")

class TicketServiceDisplay(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False
    readonly_fields = ['ticket_id','name','cost','duration','timeunit']
    list_display = ("ticket_id","name","cost","duration","timeunit")
 
class LogDisplay(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False
    
    readonly_fields = ['ticket_id','requestor','updated_by','status','timestamp']
    list_display = ['ticket_id','requestor','updated_by','status','timestamp']

class VendorQuoteDisplay(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    list_display = ['vendor','ticket','submitted_at']

class VendorItemQuoteDisplay(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    readonly_display = ['quote_id','ticket_item','quoted_unit_price','quoted_total_price']
    list_display = ['quote_id','ticket_item','quoted_unit_price','quoted_total_price']

class VendorServiceQuoteDisplay(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    readonly_display = ['quote_id','ticket_service','quoted_unit_price','quoted_total_price']
    list_display = ['quote_id','ticket_service','quoted_unit_price','quoted_total_price']

admin.site.register(Role,RoleDisplay)
admin.site.register(User,UserDisplay)
admin.site.register(Company)
admin.site.register(Department)
admin.site.register(Category)
admin.site.register(Ticket,TicketDisplay)
admin.site.register(TicketItem,TicketItemDisplay)
admin.site.register(TicketService,TicketServiceDisplay)
admin.site.register(ApproverLog,LogDisplay)
admin.site.register(Vendor)
admin.site.register(VendorQuote,VendorQuoteDisplay)
admin.site.register(VendorItemQuote,VendorItemQuoteDisplay)
admin.site.register(VendorServiceQuote,VendorServiceQuoteDisplay)


