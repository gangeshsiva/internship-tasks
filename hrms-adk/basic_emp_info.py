from pymongo import MongoClient
from google.adk.tools import FunctionTool
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

try:
    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    
    # Select database and collection
    db = client["ABG-Cloud"]
    collection = db["mast_employees"]

except Exception as e:
    print("mongo db connection failed",e)
    raise 

def obBasicInformation(basicinfo):
    basin={}
    for key, value in basicinfo.items():
        try:
            if "oSalId" in key:
                query={'_id':value}
                collection = db["mast_salutations"]
                documents = collection.find(query)
                sal = documents[0]
                pair = {'cSalutationName':sal['cSalutationName']}
                basin["oSalId"] = pair
            elif 'oGenderId' in key:
                query={'_id':value}
                collection = db["mast_genders"]
                documents = collection.find(query)
                gen= documents[0]
                pair = {'cGenderName':gen['cGenderName']}
                basin["oGenderId"] = pair
            elif 'oMaritalStatusId' in key:
                query={'_id':value}
                collection = db["mast_marital_statuss"]
                documents = collection.find(query)
                mar= documents[0]
                pair = {'cMaritalStatusName':mar['cMaritalStatusName']}
                basin["oMaritalStatusId"] = pair
            elif 'oDepartmentId' in key:
                query={'_id':value}
                collection = db["mast_departments"]
                documents = collection.find(query)
                dept= documents[0]
                pair = {
                    'cDepartmentName':dept['cDepartmentName'],
                    'cDepartmentShortName':dept['cDepartmentShortName'],
                    'cDepartmentWiseGraceTime':dept['cDepartmentWiseGraceTime']
                        }
                basin["oDepartmentId"] = pair
            elif 'oDesignationId' in key:
                query={'_id':value}
                collection = db["hrms_mast_designations"]
                documents = collection.find(query)
                des= documents[0]
                pair = {
                    'cDesignationName':des['cDesignationName'],
                    'cDesignationShortName':des['cDesignationShortName']
                        }
                basin["oDesignationId"] = pair
            elif 'oBranchId' in key:
                query={'_id':value}
                collection = db["mast_branches"]
                documents = collection.find(query)
                branch= documents[0]
                pair = {
                    'cName':branch['cName'],
                    'cShortName':branch['cShortName'],
                    'cAddress':branch['cAddress'],
                    'cPhoneNumber':branch['cPhoneNumber'],
                    'cMobileNumber':branch['cMobileNumber'],
                    'cCreatedIPAddress':branch['cCreatedIPAddress'],
                    'cCity':branch['cCity'],
                    'cPincode':branch['cPincode'],
                    'bIsMainBranch':branch['bIsMainBranch'],
                    'cPFPrefix':branch['cPFPrefix'],
                    'cPrintName':branch['cPrintName']
                        }
                basin["oBranchId"] = pair
            elif 'oEmployeeTypeId' in key:
                query={'_id':value}
                collection = db["hrms_mast_employee_types"]
                documents = collection.find(query)
                emptype= documents[0]
                pair = {"cEmployeeType":emptype["cEmployeeType"]}
                basin["oEmployeeTypeId"] = pair
            elif 'oEmploymentCategoryId' in key:
                query={'_id':value}
                collection = db["mast_employment_categories"]
                documents = collection.find(query)
                empcat= documents[0]
                pair = {
                    "cEmploymentCategoryName":empcat["cEmploymentCategoryName"],
                    "iSortOrder":empcat["iSortOrder"],
                    "cIconClass":empcat["cIconClass"],
                    "bIsMigratedFromSQL":empcat["bIsMigratedFromSQL"],
                    "iSQLEmp_Cat_id":empcat["iSQLEmp_Cat_id"],
                    "iSQLEmp_Type_id":empcat["iSQLEmp_Type_id"],
                        }
                basin["oEmploymentCategoryId"] = pair
            elif 'oGradeId' in key:
                query={'_id':value}
                collection = db["hrms_mast_grades"]
                documents = collection.find(query)
                grade= documents[0]
                pair = {
                    "cGradeName":grade["cGradeName"],
                    "iGrade":grade["iGrade"],
                    "iSortOrder":grade["iSortOrder"]
                        }
                basin["oGradeId"] = pair
            elif 'oWorkModeId' in key:
                query={'_id':value}
                collection = db["hrms_mast_work_modes"]
                documents = collection.find(query)
                workmod= documents[0]
                pair = {
                    "cWorkModeName":workmod["cWorkModeName"],
                    "cShortName":workmod["cShortName"],
                        }
                basin["oWorkModeId"] = pair
            else:
                basin[key] = value

        except (TypeError, AttributeError, KeyError) as e:
            # If anything fails for this key, don’t crash
            basin[key] = None
            
    return basin

def obCommunicationAddress(comminfo):
    cinfo={}
    for key, value in comminfo.items():
        try:
            if "oStateId" in key:
                query={'_id':value}
                collection = db["mast_states"]
                documents = collection.find(query)
                state = documents[0]
                pair = {
                    'cStateName':state['cStateName'],
                    'cStateShortName':state['cStateShortName']
                       }
                cinfo["oStateId"] = pair
            #elif "oCountryId" in key:
                #query={'_id':value}
                #collection = db["mast_countries"]
                #documents = collection.find(query)
                #country = documents[0]
                #pair = {
                    #country.get('cCountryName') or country.get('cCountry')
                     #    }
                #cinfo["oCountryId"] = pair
            else :
                cinfo[key] =value

        except (TypeError, AttributeError, KeyError) as e:
            # If anything fails for this key, don’t crash
            cinfo[key] = None
    
    return cinfo

def get_basic_info(employee_id: str) -> dict:
      
    query = {'cEmployeeCode': employee_id}
    out= {}

    try:
        documents = list(collection.find(query))
    except Exception as e:
        print("MongoDB query failed:", e)
        documents = []

    # Print results
    for doc in documents:
        for key,value in doc.items():
            try:
                if key == "obBasicInformation":
                    out[key] = obBasicInformation(value)
                elif key == "obCommunicationAddress" or key == "obPermanentAddress":
                    out[key] = obCommunicationAddress(value)
                elif value == [] or value is None :
                    continue    
                else:
                    out[key] = value

            except Exception as e:
                # If one field fails, skip it — don’t crash everything
                print(f"Error processing key '{key}':", e)
                continue

        for k1 in list(out.keys()):
            v1 = out[k1]

            if v1 is None:
                out.pop(k1)
                continue

            if isinstance(v1, dict):
                for k2 in list(v1.keys()):
                    v2 = v1[k2]
        
                    if v2 is None:
                        v1.pop(k2)
                        continue
    
    return out

basic_info_tool = FunctionTool(get_basic_info)
        