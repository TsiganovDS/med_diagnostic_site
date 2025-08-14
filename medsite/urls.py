from django.urls import path
from .views import patient_list, add_patient, appointment_list, add_appointment, HomeView, AboutView, ServicesView, \
    ContactsView

app_name = 'medsite'

urlpatterns = [
path('', HomeView.as_view(), name='index'),
    path('patients/', patient_list, name='patient_list'),
    path('patients/add/', add_patient, name='add_patient'),
    path('patients/<int:patient_id>/appointments/', appointment_list, name='appointment_list'),
    path('patients/<int:patient_id>/appointments/add/', add_appointment, name='add_appointment'),
    path('about/', AboutView.as_view(), name='about_the_company'),
    path('services/', ServicesView.as_view(), name='services_page'),
    path('contacts/', ContactsView.as_view(), name='contacts'),
]