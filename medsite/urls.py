from django.urls import path

from .views import (
    AboutView,
    AppointmentCreateView,
    AppointmentDeleteView,
    AppointmentDetailView,
    AppointmentListView,
    AppointmentUpdateView,
    ContactsView,
    DiagnosisCreateView,
    DiagnosisUpdateView,
    DoctorListView,
    DoctorRegistrationView,
    DoctorUpdateView,
    FeedbackView,
    HomeView,
    PatientHistoryView,
    PatientProfileUpdateView,
    ServicesView,
    SuccessView,
)

app_name = "medsite"

urlpatterns = [
    path("", HomeView.as_view(), name="index"),
    path("about/", AboutView.as_view(), name="about_the_company"),
    path("services/", ServicesView.as_view(), name="services_page"),
    path("contacts/", ContactsView.as_view(), name="contacts"),
    path("appointment-success/", SuccessView.as_view(), name="appointment_success"),
    path("appointments/list/", AppointmentListView.as_view(), name="appointment_list"),
    path("appointment/form/", AppointmentCreateView.as_view(), name="appointment_form"),
    path(
        "appointment/<int:pk>/",
        AppointmentDetailView.as_view(),
        name="appointment_detail",
    ),
    path("<int:pk>/edit/", AppointmentUpdateView.as_view(), name="appointment_edit"),
    path(
        "<int:pk>/delete/", AppointmentDeleteView.as_view(), name="appointment_delete"
    ),
    path("doctors/", DoctorListView.as_view(), name="doctors"),
    path("doctor/update/<int:pk>/", DoctorUpdateView.as_view(), name="doctor_update"),
    path("register/doctor/", DoctorRegistrationView.as_view(), name="doctor_register"),
    path("feedback/", FeedbackView.as_view(), name="form"),
    path("history/", PatientHistoryView.as_view(), name="patient_history"),
    path(
        "appointment/<int:appointment_id>/diagnosis/<int:diagnosis_id>/",
        DiagnosisUpdateView.as_view(),
        name="diagnosis_update",
    ),
    path(
        "appointment/<int:appointment_id>/diagnosis/create/",
        DiagnosisCreateView.as_view(),
        name="diagnosis_form",
    ),
    path("profile/update/", PatientProfileUpdateView.as_view(), name="update_profile"),
    path(
        "appointment/<int:appointment_id>/diagnosis/<int:diagnosis_id>/",
        DiagnosisUpdateView.as_view(),
        name="diagnosis_update",
    ),
]
