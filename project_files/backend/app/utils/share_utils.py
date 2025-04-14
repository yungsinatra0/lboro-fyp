from sqlmodel import Session, select
from ..models import Vaccine, Allergy, Medication, HealthData, MedicalHistory, LabResult, AllergyResponse, MedicationResponse, HealthDataResponse, MedicalHistoryResponse, LabTest, LabTestResponse, LabResultResponse, VaccineResponse, MedicalHistoryResponseLab

def get_item_data(grouped_items, session: Session):
    items_data = {}
    
    if "Vaccine" in grouped_items:
        vaccines = session.exec(
            select(Vaccine).where(Vaccine.id.in_(grouped_items["Vaccine"]))
        ).all()
        
        for vaccine in vaccines:
            vaccine_data = vaccine.model_dump(exclude={"date_received, user, file"})
            vaccine_data["date_received"] = vaccine.date_received  
            
            vaccine = VaccineResponse(
                **vaccine_data,
                file = True if vaccine.certificate else False,
            )
            
        items_data["Vaccine"] = vaccines
    
    if "Alergii" in grouped_items:
        allergies = session.exec(
            select(Allergy).where(Allergy.id.in_(grouped_items["Alergii"]))
        ).all()
        
        for allergy in allergies:
            allergy_data = allergy.model_dump(exclude={"allergens", "reactions", "severity", "date_diagnosed"})
            allergy_data["date_diagnosed"] = allergy.date_diagnosed
            
            allergy = AllergyResponse(
                **allergy_data,
                allergens=[allergen.name for allergen in allergy.allergens],
                reactions=[reaction.name for reaction in allergy.reactions],
                severity=allergy.severity.name if allergy.severity else None,
            )
            
        items_data["Alergii"] = allergies
        
    if "Medicamente" in grouped_items:
        medications = session.exec(
            select(Medication).where(Medication.id.in_(grouped_items["Medicamente"]))
        ).all()
        
        for medication in medications:
            medication_data = medication.model_dump(exclude={"route", "form", "date_prescribed"})
            medication_data["date_prescribed"] = medication.date_prescribed
            
            medication = MedicationResponse(
                **medication_data,
                route=medication.route.name if medication.route else None,
                form=medication.form.name if medication.form else None,
            )            
        
        items_data["Medicamente"] = medications
    
    if "Semne vitale" in grouped_items:
        healthdata = session.exec(
            select(HealthData).where(HealthData.id.in_(grouped_items["Semne vitale"]))
        ).all()
        
        for data in healthdata:
            healthdata_data = data.model_dump(exclude={"type", "date_recorded", "user"})
            healthdata_data["date_recorded"] = data.date_recorded
            
            data = HealthDataResponse(
                **healthdata_data,
                name=data.type.name if data.type else None,
                unit=data.type.unit if data.type else None,
                normal_range=data.type.normal_range if data.type else None,             
            )
            
        items_data["Semne vitale"] = healthdata
        
    if "Istoric medical" in grouped_items:
        medicalhistory = session.exec(
            select(MedicalHistory).where(MedicalHistory.id.in_(grouped_items["Istoric medical"]))
        ).all()
        
        for history in medicalhistory:
            history_data = history.model_dump(exclude={"category", "subcategory", "labsubcategory", "date_consultation", "user", "file"})
            history_data["date_consultation"] = history.date_consultation
            
            history = MedicalHistoryResponse(
                **history_data,
                category=history.category.name if history.category else None,
                subcategory=history.subcategory.name if history.subcategory else None,
                labsubcategory=history.labsubcategory.name if history.labsubcategory else None,
                file = True if history.file else False,
            )
            
        items_data["Istoric medical"] = medicalhistory

    if "Rezultate laborator" in grouped_items:
        labresults = session.exec(
            select(LabResult).where(LabResult.id.in_(grouped_items["Rezultate laborator"]))
        ).all()
    
        # Each lab results already has a .test property that points to the test it belongs to
        labtests = [result.test for result in labresults if result.test]  
        
        # Transform the lab tests to response model
        transformed_tests = []
        for test in labtests:
            # Find related results for this test
            test_results = [result for result in labresults if result.test_id == test.id]
            
            transformed_tests.append(LabTestResponse(
                **test.model_dump(exclude={"results"}),
                results=[
                    LabResultResponse(
                        **result.model_dump(exclude={"test", "user", "medicalhistory", "date_collection"}),
                        date_collection = result.date_collection,
                        medicalhistory=MedicalHistoryResponseLab(
                            id = result.medicalhistory.id,
                            file = True if result.medicalhistory.file else False,
                        )
                    ) for result in test_results
                ]
            ))
            
        items_data["Rezultate laborator"] = transformed_tests
    
    return items_data        