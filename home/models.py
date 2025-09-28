from django.db import models
from django.contrib.auth.hashers import check_password,make_password
from django.core.validators import MinValueValidator, MaxValueValidator
from multiselectfield import MultiSelectField

def vendor_directory_path(instance, filename):
    # This function will save files to: vendors/<vendor-name>/<filename>
    folder_name = instance.name.replace(" ", "_")  # Replace spaces with underscores for file safety
    return 'vendors/'+ folder_name+"/"+ filename


# Create your models here.
class Role(models.Model):
    name = models.CharField( max_length=50)
    def __str__(self):
        return self.name

class Company(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField( max_length=50)
    def __str__(self):
        return self.name

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    password = models.CharField(max_length=126)
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    def __str__(self):
        return self.email 
    
class Ticket(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Ordered', 'Ordered'),
        ('Delivered', 'Delivered'),
        ('Closed', 'Closed'),
    ]
    ticket_id = models.CharField(max_length=200, unique=True) #
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending') #
    title = models.CharField(max_length=100) #
    category = models.ForeignKey(Category, on_delete=models.RESTRICT) #
    requestor = models.ForeignKey(User, related_name="requestor",on_delete=models.RESTRICT) #
    created_at = models.DateField(null=True, blank=True) #
    company = models.ForeignKey(Company, on_delete=models.RESTRICT, null=True) #
    department = models.ForeignKey(Department, on_delete=models.RESTRICT, null=True) #
    required_by = models.DateField(auto_now=False, auto_now_add=False) #
    description = models.TextField(blank=True) #
    justification = models.TextField() #
    estimated_delivery = models.DateField(auto_now=False, auto_now_add=False,null=True)
    total_estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    comment = models.TextField(blank=True)
    rfq_sent = models.BooleanField(default=False)
    def __str__(self):
        return self.ticket_id 

class TicketItem(models.Model):
    UNITS = [ 
        #  ! MOREEEEEEEEE QUANTITIES
        ('pcs','pcs'),
        ('kg','kg'),
        ('liter','liter'),
        ('box','box'),
        ('set','set'),
    ]
    ticket_id = models.ForeignKey(Ticket,  on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    budget = models.DecimalField(max_digits=10, decimal_places=2) # ? PRICING KNOWN BY EMPLOYEE OR NOT
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, choices=UNITS, default='pcs')
    
class TicketService(models.Model):
    TIMEUNITS = [ 
        #  ! MOREEEEEEEEE QUANTITIES
        ('month','month'),
        ('year','year'),
        ('day','day'),
        ('hours','hours'),
    ]
    ticket_id = models.ForeignKey(Ticket,  on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2) # ? PRICING KNOWN BY EMPLOYEE OR NOT
    duration = models.DecimalField(max_digits=10, decimal_places=1)
    timeunit = models.CharField(max_length=20, choices=TIMEUNITS, default='month')

class ApproverLog(models.Model):
    ticket_id = models.ForeignKey(Ticket,on_delete=models.RESTRICT)
    requestor = models.ForeignKey(User,related_name="requestor_log",on_delete=models.RESTRICT)
    updated_by = models.ForeignKey(User,related_name="approver_log", on_delete=models.RESTRICT)
    status = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    
class Vendor(models.Model):
    name = models.CharField(max_length=50)
    rating = models.FloatField()
    email = models.EmailField(max_length=254,unique=True)
    address = models.TextField()
    primary_contact_person = models.CharField(max_length=50)
    primary_contact_person_email = models.EmailField(max_length=254,unique=True)
    primary_contact_person_phone = models.IntegerField(validators=[MinValueValidator(0)])
    secondary_contact_person = models.CharField(max_length=50)
    secondary_contact_person_email = models.EmailField(max_length=254,unique=True)
    secondary_contact_person_phone = models.IntegerField(validators=[MinValueValidator(0)])
    payment_buffer_days = models.IntegerField()
    NDA_signed = models.BooleanField(default=False)
    onboarding_form_signed = models.BooleanField(default=False)
    FIRM_TYPE = [
        ('Sale Proprietorship', 'Sale Proprietorship'),
        ('Partnership', 'Partnership'),
        ('Limited Liability Partnership', 'Limited Liability Partnership'),
        ('Public Limited Company', 'Public Limited Company'),
        ('Private Limited Company', 'Private Limited Company'),
        ('One Person Company', 'One Person Company'),
    ]
    firm_type = models.CharField( max_length=50,choices=FIRM_TYPE)
    # Documents
    PAN = models.FileField(upload_to=vendor_directory_path, max_length=100)
    GST_registration_certificate = models.FileField(upload_to=vendor_directory_path, max_length=100)
    MSME_certificate = models.FileField(upload_to=vendor_directory_path, max_length=100)
    category = models.ManyToManyField(Category)
    reference_person = models.CharField( max_length=50)
    reference_person_number = models.IntegerField(validators=[MinValueValidator(0)])
    reference_person_email = models.EmailField(max_length=254)
    
class VendorQuote(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.RESTRICT)
    ticket = models.ForeignKey(Ticket, on_delete=models.RESTRICT)
    submitted_at = models.DateTimeField(auto_now_add=True)

class VendorItemQuote(models.Model):
    quote_id = models.ForeignKey(VendorQuote, on_delete=models.CASCADE, related_name='item_quotes')
    ticket_item = models.ForeignKey(TicketItem, on_delete=models.CASCADE)
    quoted_unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quoted_total_price = models.DecimalField(max_digits=12, decimal_places=2)

class VendorServiceQuote(models.Model):
    quote_id = models.ForeignKey(VendorQuote, on_delete=models.CASCADE, related_name='service_quotes')
    ticket_service = models.ForeignKey(TicketService, on_delete=models.CASCADE)
    quoted_unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quoted_total_price = models.DecimalField(max_digits=12, decimal_places=2)
