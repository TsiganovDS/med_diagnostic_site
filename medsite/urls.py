from django.urls import path

from medsite.views import (
    AboutView,
    AdminAppointmentCreateView,
    AdminAppointmentsListView,
    AppointmentCreateView,
    AppointmentDeleteView,
    AppointmentDetailView,
    AppointmentListView,
    AppointmentUpdateView,
    ContactsView,
    DiagnosisCreateView,
    DiagnosisDetailView,
    DiagnosisUpdateView,
    DoctorListView,
    DoctorRegistrationView,
    DoctorUpdateView,
    FeedbackView,
    HomeView,
    PatientAppointmentsView,
    PatientHistoryView,
    PatientListView,
    PatientProfileUpdateView,
    ServicesListView,
    SuccessView,
)

app_name = "medsite"

urlpatterns = [
    path("", HomeView.as_view(), name="index"),
    path("about/", AboutView.as_view(), name="about_the_company"),
    path("services/", ServicesListView.as_view(), name="services"),
    path("contacts/", ContactsView.as_view(), name="contacts"),
    path("appointment-success/", SuccessView.as_view(), name="appointment_success"),
    path("appointments/list/", AppointmentListView.as_view(), name="appointment_list"),
    path("appointment/form/", AppointmentCreateView.as_view(), name="appointment_form"),
    path(
        "appointment/form/<int:service_id>/",
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
        "<int:pk>/delete/", AppointmentDeleteView.as_view(), name="appointment_delete"
    ),
    path("doctors/", DoctorListView.as_view(), name="doctors"),
    path("doctor/update/<int:pk>/", DoctorUpdateView.as_view(), name="doctor_update"),
    path("register/doctor/", DoctorRegistrationView.as_view(), name="doctor_register"),
    path("feedback/", FeedbackView.as_view(), name="form"),
    path("history/", PatientHistoryView.as_view(), name="patient_history"),
    path(
        "appointment/<int:appointment_id>/diagnosis/<int:pk>/",
        DiagnosisUpdateView.as_view(),
        name="diagnosis_update",
    ),
    path(
        "appointment/<int:appointment_id>/diagnosis/create/",
        DiagnosisCreateView.as_view(),
        name="diagnosis_create",
    ),
    path("profile/update/", PatientProfileUpdateView.as_view(), name="update_profile"),
    path("diagnosis/<int:pk>/", DiagnosisDetailView.as_view(), name="diagnosis_detail"),
    path(
        "appointments/",
        AdminAppointmentsListView.as_view(),
        name="admin_appointment_list",
    ),
    path(
        "appointment/create/",
        AdminAppointmentCreateView.as_view(),
        name="admin_appointment_form",
    ),
    path(
        "appointment/create/<int:patient_id>/",
        AdminAppointmentCreateView.as_view(),
        name="admin_appointment_form",
    ),
    path("patients/", PatientListView.as_view(), name="patients_list"),
    path(
        "patient/<int:patient_id>/appointments/",
        PatientAppointmentsView.as_view(),
        name="patient_appointments",
    ),
]
