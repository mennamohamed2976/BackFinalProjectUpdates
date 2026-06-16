import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from orgen.models import *
import datetime

print("🌱 Beginning to seed data...")

# ===== Ministry =====
if not Ministry.objects.exists():
    ministry = Ministry.objects.create(
        national_id='12345',
        name='Ministry of Health and Population',
        email='ministry@health.gov.eg',
        phone='0220000000',
    )
    ministry.set_password('ministry123')
    MinistryToken.objects.get_or_create(ministry=ministry)
    print("✅ ministry created")
else:
    ministry = Ministry.objects.first()
    print("⚠️ ministry already created")

# ===== Hospitals =====
hospitals_data = [
    {
        'name': 'EL Kasr Al Ainy Hospital',
        'city': 'Cairo',
        'location': 'Kasr Al Ainy Street, Cairo',
        'license_number': 'LIC-001',
        'phone': '0223456789',
        'emergency_phone': '0223456790',
        'email': 'kasr@hospital.eg',
        'working_hours': '24/7',
        'hospital_type': 'حكومي',
        'password': 'hospital123',
    },
    {
        'name': 'El Sheikh Zayed Hospital',
        'city': 'Giza',
        'location': 'Sheikh Zayed City, Giza',
        'license_number': 'LIC-002',
        'phone': '0238000000',
        'emergency_phone': '0238000001',
        'email': 'zayed@hospital.eg',
        'working_hours': '24/7',
        'hospital_type': 'حكومي',
        'password': 'hospital123',
    },
    {
        'name': 'Cleopatra Hospital',
        'city': 'Cairo',
        'location': 'New Cairo, Cairo',
        'license_number': 'LIC-003',
        'phone': '0224567890',
        'emergency_phone': '0224567891',
        'email': 'cleopatra@hospital.eg',
        'working_hours': '24/7',
        'hospital_type': 'خاص',
        'password': 'hospital123',
    },
]

hospitals = []
for h_data in hospitals_data:
    password = h_data.pop('password')
    hospital, created = Hospital.objects.get_or_create(
        email=h_data['email'],
        defaults={**h_data, 'ministry': ministry, 'status': 'نشط'}
    )
    if created:
        hospital.set_password(password)
        HospitalToken.objects.get_or_create(hospital=hospital)
        print(f"✅ Hospital {hospital.name} created")
    hospitals.append(hospital)

# ===== Doctors =====
doctors_data = [
    {'name': ' Ahmed Ali', 'specialty': 'Kidney Surgery', 'phone': '01001234567', 'hospital': hospitals[0]},
    {'name': ' Sarah Khalid Hassan', 'specialty': 'Liver Surgery', 'phone': '01002345678', 'hospital': hospitals[0]},
    {'name': ' Mahmoud Abdullah', 'specialty': 'Heart Surgery', 'phone': '01003456789', 'hospital': hospitals[1]},
    {'name': ' Nora al-Din Ibrahim', 'specialty': 'Kidney Surgery ', 'phone': '01004567890', 'hospital': hospitals[1]},
    {'name': ' Hala Youssef', 'specialty': 'Liver Surgery', 'phone': '01005678901', 'hospital': hospitals[2]},
]

doctors = []
for d_data in doctors_data:
    doctor, created = Doctor.objects.get_or_create(
        name=d_data['name'],
        defaults=d_data
    )
    if created:
        print(f"✅ Doctor {doctor.name} created")
    doctors.append(doctor)

# ===== Chronic Diseases =====
diseases_names = ['السكري', 'ضغط الدم', 'الفشل الكلوي', 'تليف الكبد', 'أمراض القلب']
diseases = []
for name in diseases_names:
    disease, created = ChronicDisease.objects.get_or_create(name=name)
    diseases.append(disease)
print("✅ Chronic diseases created")


# ===== Hospital Alerts =====
for hospital in hospitals:
    if not AlertHospital.objects.filter(hospital=hospital).exists():
        AlertHospital.objects.create(
            hospital=hospital,
            message_title='تنبيه جديد',
            message=f'مرحباً بمستشفى {hospital.name} في نظام STODS',
            alert_type='معلومة'
        )
        print(f"✅ Hospital alert for {hospital.name} created")

# ===== Ministry Alert =====
if not MinistryAlert.objects.exists():
    MinistryAlert.objects.create(
        ministry=ministry,
        sender_hospital=hospitals[0],
        message_title='تقرير شهري',
        message='تم إرسال التقرير الشهري لعمليات زراعة الأعضاء',
        alert_type='تحذير',
        ALERT_Status='قيد التحقيق',
        priority='متوسطة',
    )
    print("✅ Ministry alert created")

print("\n🎉 All data seeded successfully!")
print(f"   Ministry: 1")
print(f"   Hospitals: {Hospital.objects.count()}")
print(f"   Doctors: {Doctor.objects.count()}")
print(f"   Patients: {User.objects.filter(role='patient').count()}")
print(f"   Donors: {User.objects.filter(role='donor').count()}")
print(f"   Matches: {OrganMatching.objects.count()}")
print(f"   Surgeries: {Surgery.objects.count()}")