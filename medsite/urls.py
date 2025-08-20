from django.urls import path
from .views import HomeView, AboutView, ServicesView, \
    ContactsView, AppointmentCreateView, SuccessView, AppointmentListView, AppointmentDetailView, AppointmentDeleteView, \
    AppointmentUpdateView

app_name = 'medsite'

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('about/', AboutView.as_view(), name='about_the_company'),
    path('services/', ServicesView.as_view(), name='services_page'),
    path('contacts/', ContactsView.as_view(), name='contacts'),
    path('appointment-success/', SuccessView.as_view(), name='appointment_success'),
    path('appointment/', AppointmentListView.as_view(), name='appointment_list'),
    path('appointment/create/', AppointmentCreateView.as_view(), name='appointment_create'),
    path('appointment/<int:pk>/', AppointmentDetailView.as_view(), name='appointment_detail'),
    path('<int:pk>/edit/', AppointmentUpdateView.as_view(), name='appointment_edit'),
    path('<int:pk>/delete/', AppointmentDeleteView.as_view(), name='appointment_delete'),
]