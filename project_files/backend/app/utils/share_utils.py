from sqlmodel import Session, select
from ..models import LabTest, LabTestResponse, LabResultResponse, MedicalHistoryResponseLab
import datetime

def get_item_data(grouped_items: dict, session: Session):
    items_data = {}
    
    for type_name, items in grouped_items.items():
        if type_name != "labresults":
            items_data[type_name] = items
            continue
        
        items_data['labtests'] = []
        
        for result in items:
            lab_test = session.exec(select(LabTest).where(LabTest.name == result['name'])).first()
            
            if lab_test:
                found = False
                for test_response in items_data['labtests']:
                    if test_response.id == lab_test.id:
                        test_response.results.append(LabResultResponse(
                            id=result['id'],
                            value=result['value'],
                            is_numeric=result['is_numeric'],
                            unit=result['unit'],
                            reference_range=result['reference_range'],
                            method=result['method'],
                            date_collection=datetime.datetime.strptime(result['original_date_collection'], "%d-%m-%Y").date(),
                            medicalhistory=MedicalHistoryResponseLab(
                                id=result['medicalhistory']['id'],
                                file=result['medicalhistory']['file']
                            )
                        ))
                        found = True
                        break
                if not found:
                    print("\n" + "-" * 20, result)
                    items_data['labtests'].append(LabTestResponse(
                        id=lab_test.id,
                        name=lab_test.name,
                        code=lab_test.code,
                        results=[LabResultResponse(
                            id=result['id'],
                            value=result['value'],
                            is_numeric=result['is_numeric'],
                            unit=result['unit'],
                            reference_range=result['reference_range'],
                            method=result['method'],
                            date_collection=datetime.datetime.strptime(result['original_date_collection'], "%d-%m-%Y").date(),
                            medicalhistory=MedicalHistoryResponseLab(
                                id=result['medicalhistory']['id'],
                                file=result['medicalhistory']['file']
                            )
                        )]
                    ))
            else:
                # Do something if lab_test is not found
                pass
                
    return items_data
