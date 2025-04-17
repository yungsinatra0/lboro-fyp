from sqlmodel import Session, select
from ..models import Vaccine, Allergy, Medication, HealthData, MedicalHistory, LabResult, AllergyResponse, MedicationResponse, HealthDataResponse, MedicalHistoryResponse, LabTest, LabTestResponse, LabResultResponse, VaccineResponse, MedicalHistoryResponseLab

def get_item_data(grouped_items: dict, session: Session):
    items_data = {}
    
    print("-" * 20, "\n")
    for type, value in grouped_items.items():
        print(f"Type: {type}")
        print(f"Value: {value}")        
    print("\n", "-" * 20)
    
    return items_data       