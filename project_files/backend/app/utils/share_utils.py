from sqlmodel import Session, select
from ..models import Vaccine, Allergy, Medication, HealthData, MedicalHistory, LabResult, AllergyResponse, MedicationResponse, HealthDataResponse, MedicalHistoryResponse, LabTest, LabTestResponse, LabResultResponse, VaccineResponse, MedicalHistoryResponseLab

def get_item_data(grouped_items, session: Session):
    items_data = {}
    
    print("-" * 20, "\n")
    print("Grouped items: ", grouped_items)
    print("\n", "-" * 20)
    
    return items_data       