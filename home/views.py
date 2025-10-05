from django.shortcuts import render, redirect,HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from urllib.parse import urlencode, quote_plus
from .models import *
from django.contrib import messages
from datetime import date
from decimal import Decimal
import random

def generate_rfq_message(request,ticket,vendor):
    vendors = Vendor.objects.filter(id=vendor.id)
    items = TicketItem.objects.filter(ticket_id=ticket)
    services = TicketService.objects.filter(ticket_id=ticket)

    # Email introduction
    message = (
        "Hello Team,\n\n"
        "We are currently looking for the following items and would appreciate receiving a quotation for the same by tomorrow.\n\n"
    )

    if items.exists():
        message += "Item Requirements:\n\n"
        

        for idx, item in enumerate(items, start=1):
            name = item.name[:30].ljust(30)
            detail = f"{item.name} (Est. Budget: ₹{item.budget})"[:55].ljust(55)
            qty = f"{item.quantity} {item.unit}".ljust(8)

            message += (
                f"{str(idx).ljust(4)}   |   {name}   |   {detail}   |    {qty} |\n"
            )

    else:
        message += "No item requirements listed.\n\n"

    if services.exists():
        message += "Service Requirements:\n\n"
        for idx, service in enumerate(services, start=1):
            name = service.name[:30].ljust(30)
            duration = str(service.duration).ljust(8)
            timeunit = service.timeunit.ljust(11)
            cost = f"₹{service.cost}".ljust(9)

            message += (
                f"{str(idx).ljust(4)}   |   {name}   |   {duration}   |   {timeunit}   |   {cost} |\n"
            )

    else:
        message += "\nNo service requirements listed.\n\n"
    base_url = request.build_absolute_uri('/quotation-form')
    query_params = {
        "vendorid": vendor.id,
        "ticketid": ticket.ticket_id,
    }
    full_url = f"{base_url}?{urlencode(query_params)}"
    
    message += f"Submit your quotation here: {full_url}\n"
    
    message += (
        "Looking forward to your response.\n\n"
        "Thank You!"
    )

    return message

def logout(request):
    request.session.flush()  # Clears all session data
    return redirect('/login')

def index(request):
    return render(request, "index.html")

def about(request):
    return render(request,"about.html")

def register(request):
    roles = Role.objects.all()
    companies = Company.objects.all()
    departments = Department.objects.all()

    if request.method == 'POST':
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        email = request.POST.get('email').lower()
        raw_password = request.POST.get('password')  # plain text

        role_id = request.POST.get('role')
        company_id = request.POST.get('company')
        department_id = request.POST.get('department')

        try:
            role = Role.objects.get(id=role_id)
            company = Company.objects.get(id=company_id)
            department = Department.objects.get(id=department_id)

            user = User(
                name=first_name + " " + last_name,
                email=email,  # stored as plain text
                role=role,
                company=company,
                department=department
            )
            user.set_password(raw_password)
            user.save()
            return redirect('login')

        except Exception as e:
            messages.warning(request, "Registration Failed!")

    return render(request, "register.html", {
        'roles': roles,
        'companies': companies,
        'departments': departments
    })

def login(request):
    checkLogin = request.session.get('email')
    if checkLogin is not None:
        return redirect("/dashboard")

    if request.method == "POST":
        email = request.POST.get('email').lower()
        raw_password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            if user.check_password(raw_password):
                request.session['email'] = user.email
                request.session.set_expiry(0) 
                return redirect("/dashboard")
            else:
                messages.error(request, "Invalid email or password")
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password")
            return render(request, "login.html")

    return render(request, "login.html")

def dashboard(request):
    if request.session.get('email') == None:
        return redirect("home")
    email = request.session.get('email')

    user = User.objects.get(email=email)
    if(str(user.role) == "Employee"):
        pending = Ticket.objects.filter(requestor__email=email, status='Pending').count()
        approved = Ticket.objects.filter(requestor__email=email, status='Approved').count()
        ordered = Ticket.objects.filter(requestor__email=email, status='Ordered').count()
        delivered = Ticket.objects.filter(requestor__email=email, status='Delivered').count()
        rejected = Ticket.objects.filter(requestor__email=email, status='Rejected').count()
        tickets = Ticket.objects.filter(requestor__email=email)
        return render(request,"employee.html",{'email':email,'user':user,'pending':pending,'approved':approved,'rejected':rejected,'tickets':tickets})
    elif(str(user.role) == "HOD" or str(user.role)=="Reporting Manager"):
        # Get current user's department and company
        user_company = user.company
        user_department = user.department

        # Filter tickets from same department and company
        pending = Ticket.objects.filter(
            company=user_company,
            department=user_department,
            status='Pending'
        )

        rejected = Ticket.objects.filter(
            company=user_company,
            department=user_department,
            status='Rejected'
        )

        approved = Ticket.objects.filter(
            company=user_company,
            department=user_department,
            status='Approved'
        )

        return render(request, "manager.html", {
            'user':user,
            'pending': pending,
            'rejected': rejected,
            'approved': approved
        })
    elif(str(user.role) == "Procurement"):
        user_company = user.company
        approved = Ticket.objects.filter(
            company=user_company,
            rfq_sent=False,
            status='Approved'
        )
        sent = Ticket.objects.filter(
            company=user_company,
            rfq_sent=True,
            status='Approved'
        )
        
        return render(request,"procurement.html",{'email':email,'user':user,'approved':approved,'sent':sent})

def addticket(request):
    if request.session.get('email') == None:
        return redirect("home")
    if request.method=="POST":
        ticketid = request.POST.get('ticketid')
        status = request.POST.get('status')
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        requestor_id = request.POST.get('requestor_id')
        company_id = request.POST.get('company_id')
        department_id = request.POST.get('department_id')
        required_by = request.POST.get('required_by')
        description = request.POST.get('description')
        justification = request.POST.get('justification')
        # print(ticketid)
        try:
            category = Category.objects.get(id=category_id)
            requestor = User.objects.get(id=requestor_id)
            company = Company.objects.get(id=company_id)
            department = Department.objects.get(id=department_id)

            Ticket.objects.create(
                ticket_id = ticketid,
                status = status,
                title = title,
                category = category,
                requestor = requestor,
                created_at=date.today(),
                company = company,
                department = department,
                required_by = required_by,
                description = description,
                justification = justification,
                total_estimated_cost = 0, # calculate the cost of the items and services
            )


            total_cost = 0
            ticketid = Ticket.objects.get(ticket_id=ticketid)
            
            item_index = 0
            while True:
                name = request.POST.get(f'items[{item_index}][name]')
                if not name:
                    break  # no more items
                budget = float(request.POST.get(f'items[{item_index}][budget]',0))
                quantity = int(request.POST.get(f'items[{item_index}][quantity]', 0))
                unit = request.POST.get(f'items[{item_index}][unit]', '')

                TicketItem.objects.create(
                    ticket_id=ticketid,
                    name=name,
                    budget=budget,
                    quantity=quantity,
                    unit=unit
                )
                total_cost += budget * quantity
                item_index += 1

            service_index = 0
            while True:
                name = request.POST.get(f'services[{service_index}][name]')
                if not name:
                    break  # no more services
                cost = float(request.POST.get(f'services[{service_index}][cost]', 0))
                duration = int(request.POST.get(f'services[{service_index}][duration]', 0))
                timeunit = request.POST.get(f'services[{service_index}][timeunit]', '')

                TicketService.objects.create(
                    ticket_id=ticketid,
                    name=name,
                    cost=cost,
                    duration=duration,
                    timeunit=timeunit
                )
                total_cost += cost * duration
                service_index += 1

            ticket = Ticket.objects.get(ticket_id=ticketid)
            ticket.total_estimated_cost = total_cost
            ticket.save(update_fields=['total_estimated_cost'])
            return redirect('dashboard')
        except Exception as e:
            messages.warning(request, "Failed to create ticket")
    def ticketID(cmp,dept):
        ans = "#" +"-"+ str(cmp) +"-"+ str(dept) +"-"+ str(random.randint(1000,9999)) +"-"+ date.today().strftime('%d%m%y') +"-"+ str(Ticket.objects.filter(created_at=date.today().strftime('%Y-%m-%d')).count()+1)
        return ans
    email = request.session.get('email')
    user = User.objects.get(email=email)
    categories = Category.objects.all()
    today = date.today().strftime('%d-%m-%y')
    ticketid = ticketID(user.company,user.department)

    return render(request,"addticket.html",{'email':email,'user':user,'today':today,'categories':categories,'ticketid':ticketid})

def tickets(request):
    email = request.session.get('email')
    if not email:
        return redirect("home")
    user = User.objects.get(email=email)
    role = str(user.role)
    status = request.GET.get('status', '')
    if 'status' not in request.GET:
        return redirect(f'/tickets?status={status}')

    tickets = Ticket.objects.none()  # default empty queryset

    if role == "Employee":
        tickets = Ticket.objects.filter(requestor__email=email)
        if status:
            tickets = tickets.filter(status=status)

    elif role == "Procurement":
        tickets = Ticket.objects.filter(requestor__company=user.company)
        if status:
            tickets = tickets.filter(status=status)

    elif role in ["HOD", "Reporting Manager"]:
        tickets = Ticket.objects.filter(
            requestor__department=user.department,
            requestor__company=user.company
        )
        if status:
            tickets = tickets.filter(status=status)
    else:
        tickets = Ticket.objects.none()
    return render(request, "tickets.html",{'email': email,'user': user,'tickets': tickets,'role': role})
 
def usersetting(request):
    if request.session.get('email') == None:
        return redirect("home")
    email = request.session.get('email')
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect("dashboard")
    if request.method=="POST":
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        
        full_name = f"{fname} {lname}"
        if new_password:
            user.password = make_password(new_password)  # Hash password
        user.name=full_name
        user.save()
    role = str(user.role)
    departments = Department.objects.all()
    companies = Company.objects.all()
    name_parts = user.name.split()
    return render(request, "settings.html",{'user':user,'firstname':name_parts[0],'lastname':name_parts[1],'departments':departments,'companies':companies,'role':role})

def action(request):
    if request.session.get('email') == None:
        return redirect("home")
    email = request.session.get('email')
    user = User.objects.get(email=email)
    action_type = request.GET.get('action')
    if action_type == "view":
        email = request.session.get('email')
        user = User.objects.get(email=email)
        if user.role != "Employee": 
            log = False
        ticket_id = request.GET.get("ticketid")
        ticket = Ticket.objects.get(ticket_id=ticket_id)
        items = TicketItem.objects.filter(ticket_id=ticket.id)
        services = TicketService.objects.filter(ticket_id=ticket.id)
        return render(request,"view_ticket.html",{'user':user,'ticket':ticket,'items':items,'services':services,'log':log})
    elif action_type in ["approve", "reject"]:
        
        ticket_id = request.GET.get("ticketid")
        ticket = Ticket.objects.get(ticket_id=ticket_id)
        ticket.status = "Approved" if action_type == "approve" else "Rejected"
        ticket.save()

        # Log the action
        ApproverLog.objects.create(
            ticket_id=ticket,
            requestor=ticket.requestor,
            updated_by=user,
            status=ticket.status
        )

        # Compose email
        subject = f"Ticket {ticket.ticket_id} has been {ticket.status}"
        message = (
            f"Your ticket with ID {ticket.ticket_id} has been {ticket.status.lower()} by "
            f"{user.name} ({user.email})."
        )

        # Ensure requestor email is used correctly
        recipient_email = ticket.requestor if isinstance(ticket.requestor, str) else ticket.requestor.email

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,  # Make sure this is defined in settings.py
            [recipient_email],
            fail_silently=False
        )

        return redirect("dashboard")
    if action_type == 'order':
        ticket_id = request.GET.get('ticketid')
        ticket = Ticket.objects.get(ticket_id=ticket_id)
        category = ticket.category
        vendor_list = Vendor.objects.all()
        final_vendors = Vendor.objects.filter(category=category)
        user = User.objects.get(email=email)
        ticket = Ticket.objects.get(ticket_id=ticket_id)
        items = TicketItem.objects.filter(ticket_id=ticket.id)
        services = TicketService.objects.filter(ticket_id=ticket.id)
        return render(request,"order.html",{'user':user,'ticket':ticket,'items':items,'services':services,'finalVendors':final_vendors})
    
    if action_type == 'send_rfq':
        selected_vendors = []
        for key in request.GET:
            if key.startswith('vendor'):
                if 'select' in key:
                    # Extract index from key like vendor[0][select]
                    index = key.split('[')[1].split(']')[0]
                    vendor_id_key = f'vendor[{index}][id]'
                    vendor_id = request.GET.get(vendor_id_key)
                    
                    if vendor_id:
                        try:
                            vendor = Vendor.objects.get(id=vendor_id)
                            selected_vendors.append(vendor)
                        except Vendor.DoesNotExist:
                            continue
        
        # Send RFQ emails to selected vendors
        ticket_id = request.GET.get('ticketid')
        ticket = Ticket.objects.get(ticket_id=ticket_id)

        for vendor in selected_vendors:
            if vendor.email:
                email_body = generate_rfq_message(request,ticket, vendor)
                send_mail(
                    subject=f'RFQ - Ticket {ticket.ticket_id}',
                    message=email_body,
                    from_email='your_email@domain.com',
                    recipient_list=[vendor.email],
                    fail_silently=False,
                )
        ticket.rfq_sent = True
        ticket.save()
        return redirect("dashboard")
    # Unknown action fallback
    return redirect("dashboard")

def close(request):
    ticket_id = request.GET.get('ticketid')
    ticket = Ticket.objects.get(ticket_id=ticket_id)
    ticket.status = "Closed"
    ticket.save()
    return redirect("dashboard")

def logs(request):
    if request.session.get('email') == None:
        return redirect("home")
    email = request.session.get('email') 
    user = User.objects.get(email=email)
    if str(user.role) not in ['HOD', 'Procurement', 'Reporting Manager']:
        return redirect("home")
    log = ApproverLog.objects.all() 
    return render(request,"logs.html",{'log':log})
  
def vendorForm(request):
    ticket_id = request.GET.get("ticketid")
    vendor_id = request.GET.get("vendorid")
    vendor = Vendor.objects.get(id=vendor_id)
    ticket = Ticket.objects.get(ticket_id=ticket_id)
    items = TicketItem.objects.filter(ticket_id=ticket.id)
    services = TicketService.objects.filter(ticket_id=ticket.id)
    return render(request,"vendorForm.html",{'ticket':ticket,'items':items,'services':services,'vendor':vendor})

def addQuote(request):
    if request.method == "POST":
        ticket_id = request.POST.get("ticketid")
        ticket = Ticket.objects.get(ticket_id=ticket_id)

        vendor_id = request.POST.get("vendor")
        vendor = Vendor.objects.get(id=vendor_id)

        vendor_quote = VendorQuote.objects.create(
            vendor=vendor,
            ticket=ticket
        )
        index = 0
        while True:
            item_id = request.POST.get(f"items[{index}][id]")
            if not item_id:
                break  # no more items

            quoted_unit_price = request.POST.get(f"items[{index}][quotePrice]")
            quoted_total_price = request.POST.get(f"items[{index}][total]")
            remarks = request.POST.get(f"items[{index}][remarks]")
            ticket_item = TicketItem.objects.get(id=item_id)

            VendorItemQuote.objects.create(
                quote_id=vendor_quote,
                ticket_item=ticket_item,
                quoted_unit_price=quoted_unit_price,
                quoted_total_price=quoted_total_price,
                remarks=remarks
            )

            index += 1

        # Save service quotes
        index = 0
        while True:
            service_id = request.POST.get(f"services[{index}][id]")
            if not service_id:
                break  # no more services

            quoted_unit_price = request.POST.get(f"services[{index}][quotePrice]")
            quoted_total_price = request.POST.get(f"services[{index}][total]")
            remarks = request.POST.get(f"services[{index}][remarks]")
            ticket_service = TicketService.objects.get(id=service_id)

            VendorServiceQuote.objects.create(
                quote_id=vendor_quote,
                ticket_service=ticket_service,
                quoted_unit_price=quoted_unit_price,
                quoted_total_price=quoted_total_price,
                remarks=remarks
            )

            index += 1

    return redirect("dashboard")

def viewQuote(request):
    if request.session.get('email') == None:
        return redirect("home")
    email = request.session.get('email')
    user = User.objects.get(email=email)
    dept = str(user.department)
    if dept != "Procurement":
        return redirect("home")
    ticket_id = request.GET.get("ticketid")
    ticket = Ticket.objects.get(ticket_id=ticket_id)
    items = TicketItem.objects.filter(ticket_id=ticket.id)
    services = TicketService.objects.filter(ticket_id=ticket.id)
    vendorQuotes = VendorQuote.objects.filter(ticket=ticket.id)
    
    vendor_data = {}
    for vendor_quote in vendorQuotes:
        vendor = vendor_quote.vendor
        item_quotes = VendorItemQuote.objects.filter(quote_id=vendor_quote)
        service_quotes = VendorServiceQuote.objects.filter(quote_id=vendor_quote)
        vendor_data[vendor] = {
            'item_quotes': item_quotes,
            'service_quotes': service_quotes,
        }
        total_item_price = sum([q.quoted_total_price for q in item_quotes])
        total_service_price = sum([q.quoted_total_price for q in service_quotes])
        grand_total = total_item_price + total_service_price
    return render(request,"viewQuote.html",{'ticket': ticket,'items': items,'services': services,'vendor_data': vendor_data,'grand_total':grand_total})