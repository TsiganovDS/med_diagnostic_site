from django.test import TestCase
from django.urls import reverse


class TestMedsiteUrls(TestCase):
    def test_home_url(self):
        url = reverse("medsite:index")
        self.assertEqual(url, "/")

    def test_about_url(self):
        url = reverse("medsite:about_the_company")
        self.assertEqual(url, "/about/")

    def test_services_url(self):
        url = reverse("medsite:services")
        self.assertEqual(url, "/services/")

    def test_contacts_url(self):
        url = reverse("medsite:contacts")
        self.assertEqual(url, "/contacts/")

    def test_appointment_success_url(self):
        url = reverse("medsite:appointment_success")
        self.assertEqual(url, "/appointment-success/")

    def test_appointment_list_url(self):
        url = reverse("medsite:appointment_list")
        self.assertEqual(url, "/appointments/list/")

    def test_appointment_form_url(self):
        url = reverse("medsite:appointment_form")
        self.assertEqual(url, "/appointment/form/")

    def test_appointment_detail_url(self):
        url = reverse("medsite:appointment_detail", kwargs={"pk": 1})
        self.assertEqual(url, "/appointment/1/")

    def test_appointment_edit_url(self):
        url = reverse("medsite:appointment_edit", kwargs={"pk": 1})
        self.assertEqual(url, "/1/edit/")

    def test_appointment_delete_url(self):
        url = reverse("medsite:appointment_delete", kwargs={"pk": 1})
        self.assertEqual(url, "/1/delete/")

    def test_doctors_list_url(self):
        url = reverse("medsite:doctors")
        self.assertEqual(url, "/doctors/")

    def test_doctor_update_url(self):
        url = reverse("medsite:doctor_update", kwargs={"pk": 1})
        self.assertEqual(url, "/doctor/update/1/")

    def test_doctor_registration_url(self):
        url = reverse("medsite:doctor_register")
        self.assertEqual(url, "/register/doctor/")

    def test_feedback_url(self):
        url = reverse("medsite:form")
        self.assertEqual(url, "/feedback/")

    def test_patient_history_url(self):
        url = reverse("medsite:patient_history")
        self.assertEqual(url, "/history/")

    def test_diagnosis_update_url(self):
        url = reverse("medsite:diagnosis_update", kwargs={"appointment_id": 1, "pk": 1})
        self.assertEqual(url, "/appointment/1/diagnosis/1/")

    def test_diagnosis_create_url(self):
        url = reverse("medsite:diagnosis_create", kwargs={"appointment_id": 1})
        self.assertEqual(url, "/appointment/1/diagnosis/create/")

    def test_profile_update_url(self):
        url = reverse("medsite:update_profile")
        self.assertEqual(url, "/profile/update/")

    def test_diagnosis_detail_url(self):
        url = reverse("medsite:diagnosis_detail", kwargs={"pk": 1})
        self.assertEqual(url, "/diagnosis/1/")

    def test_admin_appointments_list_url(self):
        url = reverse("medsite:admin_appointment_list")
        self.assertEqual(url, "/appointments/")

    def test_admin_appointment_create_url(self):
        url = reverse("medsite:admin_appointment_form")
        self.assertEqual(url, "/appointment/create/")

    def test_patients_list_url(self):
        url = reverse("medsite:patients_list")
        self.assertEqual(url, "/patients/")

    def test_patient_appointments_url(self):
        url = reverse("medsite:patient_appointments", kwargs={"patient_id": 1})
        self.assertEqual(url, "/patient/1/appointments/")

    def test_admin_appointment_create_with_patient(self):
        url = reverse("medsite:admin_appointment_form", kwargs={"patient_id": 1})
        self.assertEqual(url, "/appointment/create/1/")

    def test_appointment_form_with_service(self):
        url = reverse("medsite:appointment_form", kwargs={"service_id": 1})
        self.assertEqual(url, "/appointment/form/1/")

    def test_all_urls_return_200(self):
        urls = [
            "medsite:index",
            "medsite:about_the_company",
            "medsite:services",
            "medsite:contacts",
            "medsite:appointment_success",
        ]

        for url_name in urls:
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)

    def test_url_resolution(self):
        # Проверка разрешения URL
        from django.urls import resolve

        # Пример проверки для одного URL
        resolved = resolve("/appointments/list/")
        self.assertEqual(resolved.view_name, "medsite:appointment_list")
