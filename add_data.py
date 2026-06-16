import os
import django
import json
import random
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from orgen.models import *

print("🌱 Beginning to add recipients from the JSON file...")

hospital = Hospital.objects.first()
doctor = Doctor.objects.first()

if not hospital:
    print("❌ No hospital found in the database!")
    exit()

with open("transplant_2000_enriched.json", "r", encoding="utf-8") as f:
    data = json.load(f)

recipients = data.get("recipients", [])
print(f"📋 Number of recipients: {len(recipients)}")

created = 0
skipped = 0

for i, r in enumerate(recipients):
    recipient_id = r.get("recipient_id")

    if PatientMedicalProfile.objects.filter(recipient_id=recipient_id).exists():
        skipped += 1
        continue

    age = r.get("age", 30)
    birth_year = date.today().year - age
    birthdate = date(birth_year, random.randint(1, 12), random.randint(1, 28))

    blood_type = r.get("blood_type", "O")
    # if blood_type not in ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]:
    #     blood_type = blood_type + "+"

    sex = r.get("sex", "M")
    gender = "ذكر" if sex in ["M", "Male", "male"] else "انثي"
    generated_national_id = f"8{str(i+1).zfill(13)}"

    actual_national_id = r.get("national_id", generated_national_id)

    # User.set_password(actual_national_id[-4:])
    # User.save()

    try:
        user = User.objects.create(
            national_id=actual_national_id,
            first_name=r.get("first_name", ""),
            last_name=r.get("last_name", ""),
            role=r.get("role", ""),
            phone=r.get("phone", ""),
            email=r.get("email", ""),
            status="جاهز",
            birthdate=birthdate,
            blood_type=blood_type,
            gender=gender,
            height_cm=r.get("height_cm") or 170.0,
            weight_kg=r.get("weight_kg") or 70.0,
            HLA_A_1=r.get("HLA_A_1", ""),
            HLA_A_2=r.get("HLA_A_2", ""),
            HLA_B_1=r.get("HLA_B_1", ""),
            HLA_B_2=r.get("HLA_B_2", ""),
            HLA_DR_1=r.get("HLA_DR_1", ""),
            HLA_DR_2=r.get("HLA_DR_2", ""),
            PRA=float(r.get("PRA", 0)),
            CMV_status=r.get("CMV_status", "").lower() == "positive",
            EBV_status=r.get("EBV_status", "").lower() == "positive",
            medical_record_number=recipient_id,
            hospital=hospital,
            supervisor_doctor=doctor,
        )
        user.set_password(actual_national_id[-4:])  # ✅ على الـ instance
        user.save()

        # ✅ VitalSigns من داخل الـ dict
        vital_data = r.get("vital_signs", {}) or {}
        VitalSigns.objects.create(
            user=user,
            heart_rate=vital_data.get("heart_rate"),
            blood_pressure=vital_data.get("blood_pressure"),
            respiratory_rate=vital_data.get("respiratory_rate"),
            temperature_c=vital_data.get("temperature_c"),
            oxygen_saturation=vital_data.get("oxygen_saturation"),
        )

        # ✅ Medicines
        for med in r.get("medicines", []):
            Medicine.objects.create(
                user=user,
                name=med.get("name", ""),
                frequency_per_day=med.get("frequency_per_day", 1),
                notes=med.get("notes", ""),
            )

        # ✅ Allergies
        for allergy in r.get("allergies", []):
            Allergy.objects.create(
                user=user,
                name=allergy.get("name", ""),
                severity=allergy.get("severity", "منخفض"),
            )

        # ✅ Chronic Diseases
        for disease in r.get("chronic_diseases", []):
            disease_name = disease.get("name", "") if isinstance(disease, dict) else disease
            chronic, _ = ChronicDisease.objects.get_or_create(name=disease_name)
            UserChronicDisease.objects.create(
                user=user,
                disease=chronic,
                severity=disease.get("severity", "متوسط") if isinstance(disease, dict) else "متوسط",
            )

        # ✅ PatientMedicalProfile
        organ_mapping = {
            "lung": "lung_left",
            "lung_left": "lung_left",
            "lung_right": "lung_right",
            "lung_lobe": "lung_lobe",
        }
        organ_needed_raw = r.get("organ_needed", "kidney_left")
        organ_needed = organ_mapping.get(organ_needed_raw, organ_needed_raw)

        dialysis = r.get("dialysis_duration_days")
        meld = r.get("MELD_score")
        lung = r.get("lung_severity_score")

        KIDNEY_ORGANS = ["kidney", "kidney_right", "kidney_left"]
        LIVER_ORGANS  = ["liver", "liver_lobe"]
        LUNG_ORGANS   = ["lung_right", "lung_left", "lung_lobe"]

        PatientMedicalProfile.objects.create(
            patient=user,
            organ_needed=organ_needed,
            recipient_id=recipient_id,
            urgency_level=r.get("urgency_level", "medium"),
            waitlist_time_days=r.get("waitlist_time_days", 0),
            dialysis_duration_days=dialysis if dialysis and dialysis > 0 and organ_needed in KIDNEY_ORGANS else None,
            MELD_score=meld if meld and meld > 0 and organ_needed in LIVER_ORGANS else None,
            lung_severity_score=lung if lung and lung > 0 and organ_needed in LUNG_ORGANS else None,
        )

        created += 1
        if created % 100 == 0:
            print(f"✅ Created {created} patients...")

    except Exception as e:
        print(f"❌ failed to add {recipient_id}: {e}")
        skipped += 1
        continue

print(f"\n🎉 Done")
print(f"   ✅ created: {created}")
print(f"   ⚠️ skipped: {skipped}")
print(f"   📊 total patients: {User.objects.filter(role='patient').count()}")