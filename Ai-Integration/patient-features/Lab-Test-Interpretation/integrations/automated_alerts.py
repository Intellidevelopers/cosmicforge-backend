
import asyncio
from flask_mail import Mail, Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Patient, Doctor
import logging

mail = Mail()
logger = logging.getLogger(__name__)

async def check_critical_results(interpretation, lab_results, patient_id):
    critical_thresholds = {
        'glucose': {'low': 70, 'high': 200, 'unit': 'mg/dL'},
        'hemoglobin': {'low': 7, 'high': 20, 'unit': 'g/dL'},
        'white_blood_cell_count': {'low': 3000, 'high': 15000, 'unit': 'cells/µL'},
        'platelet_count': {'low': 50000, 'high': 450000, 'unit': 'platelets/µL'},
        'potassium': {'low': 3.0, 'high': 5.5, 'unit': 'mEq/L'},
        'sodium': {'low': 130, 'high': 150, 'unit': 'mEq/L'},
        'creatinine': {'low': 0.6, 'high': 1.2, 'unit': 'mg/dL'},
        'troponin': {'low': None, 'high': 0.04, 'unit': 'ng/mL'},
        'prothrombin_time': {'low': None, 'high': 13.5, 'unit': 'seconds'},
        'partial_thromboplastin_time': {'low': None, 'high': 35, 'unit': 'seconds'},
        'blood_ph': {'low': 7.35, 'high': 7.45, 'unit': None},
        'pco2': {'low': 35, 'high': 45, 'unit': 'mmHg'},
        'po2': {'low': 80, 'high': None, 'unit': 'mmHg'},
        'hco3': {'low': 22, 'high': 26, 'unit': 'mEq/L'}
    }

    critical_results = []
    for test, result in lab_results.items():
        if test in critical_thresholds:
            threshold = critical_thresholds[test]
            if (threshold['low'] is not None and result < threshold['low']) or \
               (threshold['high'] is not None and result > threshold['high']):
                unit = f" {threshold['unit']}" if threshold['unit'] else ""
                critical_results.append(f"{test}: {result}{unit}")

    if critical_results:
        await send_alert(patient_id, critical_results, interpretation)
        return True
    return False

async def send_alert(patient_id, critical_results, interpretation):
    try:
        patient = await get_patient_info(patient_id)
        doctor = await get_primary_doctor(patient_id)

        subject = f"URGENT: Critical Lab Results for Patient {patient_id}"
        body = f"""
        Critical lab results detected for patient {patient['name']} (ID: {patient_id}):

        {', '.join(critical_results)}

        Full interpretation:
        {interpretation}

        Please review and take appropriate action immediately.

        Patient contact: {patient['phone']}
        """

        msg = Message(subject, recipients=[doctor['email']])
        msg.body = body

        await asyncio.to_thread(mail.send, msg)
        logger.info(f"Alert sent for patient {patient_id} to doctor {doctor['name']}")
    except Exception as e:
        logger.error(f"Failed to send alert for patient {patient_id}: {str(e)}")

async def get_patient_info(patient_id):
    async with AsyncSession() as session:
        result = await session.execute(select(Patient).filter_by(id=patient_id))
        patient = result.scalar_one_or_none()
        if patient:
            return {'name': patient.name, 'phone': patient.phone}
        else:
            logger.error(f"Patient with ID {patient_id} not found")
            raise ValueError(f"Patient with ID {patient_id} not found")

async def get_primary_doctor(patient_id):
    async with AsyncSession() as session:
        result = await session.execute(select(Doctor).join(Patient).filter(Patient.id == patient_id))
        doctor = result.scalar_one_or_none()
        if doctor:
            return {'name': doctor.name, 'email': doctor.email}
        else:
            logger.error(f"Primary doctor for patient with ID {patient_id} not found")
            raise ValueError(f"Primary doctor for patient with ID {patient_id} not found")
