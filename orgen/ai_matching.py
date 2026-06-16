import requests
from django.conf import settings
from .models import (
    User, PatientMedicalProfile, OrganMatching
)


def build_recipient_data(profile):
    p = profile.patient
    return {
        "recipient_id": profile.recipient_id or str(p.id),
        "organ_needed": profile.organ_needed,
        "blood_type": p.blood_type.replace("+", "").replace("-", "").strip(),
        "age": calculate_age(p.birthdate),
        "sex": "M" if p.gender == "ذكر" else "F",
        "height_cm": p.height_cm or 170.0,
        "weight_kg": p.weight_kg or 70.0,
        "BMI": p.bmi or 24.0,
        "HLA_A_1": p.HLA_A_1 or "",
        "HLA_A_2": p.HLA_A_2 or "",
        "HLA_B_1": p.HLA_B_1 or "",
        "HLA_B_2": p.HLA_B_2 or "",
        "HLA_DR_1": p.HLA_DR_1 or "",
        "HLA_DR_2": p.HLA_DR_2 or "",
        "PRA": int(p.PRA or 0),
        "CMV_status": "positive" if p.CMV_status else "negative",
        "EBV_status": "positive" if p.EBV_status else "negative",
        "urgency_level": profile.urgency_level or "medium",
        "waitlist_time_days": profile.waitlist_time_days or 0,
        "dialysis_duration_days": profile.dialysis_duration_days,
        "MELD_score": profile.MELD_score,
        "lung_severity_score": profile.lung_severity_score,
    }


def calculate_age(birthdate):
    if not birthdate:
        return 30
    from datetime import date
    today = date.today()
    return today.year - birthdate.year - (
        (today.month, today.day) < (birthdate.month, birthdate.day)
    )


def trigger_ai_matching(donor_user):
    try:
        donor_profile = donor_user.donor_profile
    except Exception:
        print("Donor profile not found")
        return None

    recipients_qs = PatientMedicalProfile.objects.filter(
        organ_needed=donor_profile.organ_available
    ).select_related('patient')

    if not recipients_qs.exists():
        print("No recipients found for this organ")
        return None

    donor_data = {
        "donor_id": donor_profile.donor_code or str(donor_user.id),
        "organ_type": donor_profile.organ_available,
        "blood_type": donor_user.blood_type.replace("+", "").replace("-", "").strip(),
        "age": calculate_age(donor_user.birthdate),
        "sex": "M" if donor_user.gender == "ذكر" else "F",
        "height_cm": donor_user.height_cm or 170.0,
        "weight_kg": donor_user.weight_kg or 70.0,
        "BMI": donor_user.bmi or 24.0,
        "HLA_A_1": donor_user.HLA_A_1 or "",
        "HLA_A_2": donor_user.HLA_A_2 or "",
        "HLA_B_1": donor_user.HLA_B_1 or "",
        "HLA_B_2": donor_user.HLA_B_2 or "",
        "HLA_DR_1": donor_user.HLA_DR_1 or "",
        "HLA_DR_2": donor_user.HLA_DR_2 or "",
        "PRA": int(donor_user.PRA or 0),
        "CMV_status": "positive" if donor_user.CMV_status else "negative",
        "EBV_status": "positive" if donor_user.EBV_status else "negative",
    }


    recipients_list = [
        build_recipient_data(profile)
        for profile in recipients_qs
    ]

    payload = {
        "donor": donor_data,
        "recipients": recipients_list,
        "top_k": 1
    }

    try:
        response = requests.post(
            f"{settings.AI_SERVICE_URL}/api/matching/",
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        ai_result = response.json()

        save_matching_results(donor_user, ai_result)
        return ai_result

    except requests.exceptions.RequestException as e:
        print(f"AI Matching Error: {e}")
        return None


def save_matching_results(donor_user, ai_result):
    top_matches = ai_result.get("top_matches", [])
    organ_type = donor_user.donor_profile.organ_available

    for match in top_matches:
        recipient_id = match.get("recipient_id")

        try:
            profile = PatientMedicalProfile.objects.get(recipient_id=recipient_id)
            patient = profile.patient
        except PatientMedicalProfile.DoesNotExist:
            try:
                patient = User.objects.get(id=recipient_id)
            except User.DoesNotExist:
                continue

        OrganMatching.objects.update_or_create(
            patient=patient,
            donor=donor_user,
            defaults={
                "organ_type": organ_type,
                "match_percentage": match.get("score"),
                "ai_result": match,
                "status": "تحت المراجعه"
            }
        )