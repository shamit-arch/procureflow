from django.contrib import admin
from django.urls import path
from home import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("",views.index,name="home"),
    path("about",views.about,name="about"),
    path("register",views.register,name="register"),
    path("login",views.login,name="login"),
    path("dashboard",views.dashboard,name="dashboard"),
    path("addticket",views.addticket,name="addticket"),
    path("tickets",views.tickets,name="tickets"),
    path("setting",views.usersetting,name="usersetting"),
    path("action",views.action,name="action"),
    path("close",views.close,name="close"),
    path("logs",views.logs,name="logs"),
    path("logout",views.logout,name="logout"),
    path("quotation-form",views.vendorForm,name="vendorForm"),
    path("addquote",views.addQuote,name="addQuote"),
    path("viewquote",views.viewQuote,name="viewQuote"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
