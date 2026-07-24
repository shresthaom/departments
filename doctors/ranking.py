from django.db.models import Max
from .models import Doctor

# AHP weights for each ranking criterion
AHP_WEIGHTS = {
    "availability": 0.507,
    "experience": 0.254,
    "qualification": 0.168,
    "fee": 0.073,
}

# Qualification levels used for normalization
QUALIFICATION_LEVELS = {
    "MBBS": 1,
    "BDS": 1,
    "MD": 2,
    "MS": 2,
    "MDS": 2,
    "FCPS": 2,
    "DM": 3,
    "MCh": 3,
}

def calculate_score_with_breakdown(doctor):
    # Availability score
    availability_score = 1 if doctor.a_status else 0
    # Normalize experience against the most experienced doctor
    max_experience = (
        Doctor.objects.aggregate(
            Max("experience_years")
        )["experience_years__max"] or 1
    )
    
    experience_score = (
        doctor.experience_years / max_experience
    )

    # Identify and normalize the doctor's highest qualification
    doctor_qualifications = [
        q.strip().upper()
        for q in (
            doctor.qualification or ""
        ).replace("(", ",").replace(")", "").split(",")
    ]

    max_qualification_level = max(
        QUALIFICATION_LEVELS.values()
    )

    highest_level = 0
    qualification_name = ""

    for qualification, level in QUALIFICATION_LEVELS.items():

        if (
            qualification in doctor_qualifications
            and level > highest_level
        ):
            highest_level = level
            qualification_name = qualification

    qualification_score = (
        highest_level / max_qualification_level
    )

    # Fee affordability score
    if doctor.fees <= 500:
        fee_score = 1.0

    elif doctor.fees <= 1000:
        fee_score = 0.7

    elif doctor.fees <= 1500:
        fee_score = 0.4

    else:
        fee_score = 0.0

    # Calculate weighted points
    availability_points = (
        AHP_WEIGHTS["availability"]
        * availability_score
        * 100
    )

    experience_points = (
        AHP_WEIGHTS["experience"]
        * experience_score
        * 100
    )

    qualification_points = (
        AHP_WEIGHTS["qualification"]
        * qualification_score
        * 100
    )

    fee_points = (
        AHP_WEIGHTS["fee"]
        * fee_score
        * 100
    )

    # Calculate the final recommendation score
    score = (
        availability_points
        + experience_points
        + qualification_points
        + fee_points
    )

    # Score breakdown
    breakdown = [
        (
            "Availability",
            round(availability_points, 1),
        ),
        (
            "Experience",
            round(experience_points, 1),
        ),
        (
            "Qualification",
            round(qualification_points, 1),
            qualification_name,
        ),
        (
            "Affordable Fee",
            round(fee_points, 1),
        ),
    ]

    return round(score), breakdown