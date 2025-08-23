from django.urls import path

from .views import (AboutView, AppointmentCreateView, AppointmentDeleteView,
                    AppointmentDetailView, AppointmentListView,
                    AppointmentUpdateView, ContactsView, HomeView,
                    ServicesView, SuccessView, DoctorListView, DoctorUpdateView, DoctorRegistrationView, FeedbackView)

app_name = "medsite"

urlpatterns = [
    path("", HomeView.as_view(), name="index"),
    path("about/", AboutView.as_view(), name="about_the_company"),
    path("services/", ServicesView.as_view(), name="services_page"),
    path("contacts/", ContactsView.as_view(), name="contacts"),
    path("appointment-success/", SuccessView.as_view(), name="appointment_success"),
    path('appointments/list/', AppointmentListView.as_view(), name='appointment_list'),
    path(
        "appointment/create/",
        AppointmentCreateView.as_view(),
        name="appointment_form",
    ),
    path(
        "appointment/<int:pk>/",
        AppointmentDetailView.as_view(),
        name="appointment_detail",
    ),
    path("<int:pk>/edit/", AppointmentUpdateView.as_view(), name="appointment_edit"),
    path(
        "<int:pk>/delete/", AppointmentDeleteView.as_view(), name="appointment_delete"),
    path('doctors/', DoctorListView.as_view(), name='doctors'),
    path('doctor/update/<int:pk>/', DoctorUpdateView.as_view(), name='doctor_update'),
    path('register/doctor/', DoctorRegistrationView.as_view(), name='doctor_register'),
    path('feedback/', FeedbackView.as_view(), name='form'),
 ]
