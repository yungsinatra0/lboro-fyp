from sqlmodel import Session, select
from ..models import Vaccine, Allergy, Medication, HealthData, MedicalHistory, LabResult, AllergyResponse, MedicationResponse, HealthDataResponse, MedicalHistoryResponse, LabTest, LabTestResponse, LabResultResponse

def get_item_data(grouped_items, session: Session):
    items_data = {}
    
    if "vaccine" in grouped_items:
        items_data["vaccines"] = session.exec(
            select(Vaccine).where(Vaccine.id.in_(grouped_items["vaccine"]))
        ).all()
    
    if "allergy" in grouped_items:
        allergies = session.exec(
            select(Allergy).where(Allergy.id.in_(grouped_items["allergy"]))
        ).all()
        
        for allergy in allergies:
            allergy = AllergyResponse(
                **allergy.model_dump(exclude={"allergens", "reactions", "severity"}),
                allergens=[allergen.name for allergen in allergy.allergens],
                reactions=[reaction.name for reaction in allergy.reactions],
                severity=allergy.severity.name if allergy.severity else None,
            )
            
        items_data["allergies"] = allergies
        
    if "medication" in grouped_items:
        medications = session.exec(
            select(Medication).where(Medication.id.in_(grouped_items["medication"]))
        ).all()
        
        for medication in medications:
            medication = MedicationResponse(
                **medication.model_dump(exclude={"route", "form"}),
                route=medication.route.name if medication.route else None,
                form=medication.form.name if medication.form else None,
            )            
        
        items_data["medications"] = medications
    
    if "healthdata" in grouped_items:
        healthdata = session.exec(
            select(HealthData).where(HealthData.id.in_(grouped_items["healthdata"]))
        ).all()
        
        for data in healthdata:
            data = HealthDataResponse(
                **data.model_dump(exclude={"type"}),
                name=data.type.name if data.type else None,
                unit=data.type.unit if data.type else None,
                normal_range=data.type.normal_range if data.type else None,                
            )
            
        items_data["healthdata"] = healthdata
        
    if "medicalhistory" in grouped_items:
        medicalhistory = session.exec(
            select(MedicalHistory).where(MedicalHistory.id.in_(grouped_items["medicalhistory"]))
        ).all()
        
        for history in medicalhistory:
            history = MedicalHistoryResponse(
                **history.model_dump(exclude={"category", "subcategory", "labsubcategory"}),
                category=history.category.name if history.category else None,
                subcategory=history.subcategory.name if history.subcategory else None,
                labsubcategory=history.labsubcategory.name if history.labsubcategory else None,
            )

    if "labtests" in grouped_items:
        labtests = session.exec(
            select(LabTest).where(LabTest.id.in_(grouped_items["labtests"]))
        ).all()
        
        for test in labtests:
            labresults = session.exec(
                select(LabResult).where(LabResult.id.in_(grouped_items["labresult"]), LabResult.test_id == test.id)
            ).all()
            
            test = LabTestResponse(
                **test.model_dump(exclude={"results"}),
                results=[
                    LabResultResponse(
                        **result.model_dump(exclude={"test", "user", "medicalhistory"}),
                        medicalhistory=MedicalHistoryResponse(
                            **result.medicalhistory.model_dump(exclude={"user", "file", "labresults", "category", "subcategory", "labsubcategory"}),
                            file = True if result.medicalhistory.file else False,
                            category = result.medicalhistory.category.name if result.medicalhistory.category else None,
                            subcategory = result.medicalhistory.subcategory.name if result.medicalhistory.subcategory else None,
                            labsubcategory = result.medicalhistory.labsubcategory.name if result.medicalhistory.labsubcategory else None,
                            ),
                    ) for result in labresults
                ]
            )
            
        items_data["labtests"] = labtests
    
    return items_data        