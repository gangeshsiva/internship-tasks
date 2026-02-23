from pymongo import MongoClient
from google.adk.tools import FunctionTool
from dotenv import load_dotenv
import os
from bson import ObjectId
import json
from datetime import datetime, date

load_dotenv()

def mongo_connection():
    MONGO_URI = os.getenv("MONGO_URI")

    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        
        # Select database and collection
        db = client["ABG-Cloud"]
        collection = db["mast_employees"]
        return collection,db

    except Exception as e:
        print("mongo db connection failed",e)
        raise 

def get_reportee_info(employee_id: str) -> dict:

    print("reportee info tool selected")
    output = rf"C:\Users\gangeshvar.s\Desktop\hrms deployment\hrms-adk\{employee_id}"
    os.makedirs(output, exist_ok=True)
    file_path = os.path.join(output, "reportee_info.json") 

    if os.path.isfile(file_path):
        with open(file_path, "r") as f:
            data=json.load(f)

        print("Reportee info fetched from file cache.")
        return data

    else:
        collection,db = mongo_connection()

        query = {'cEmployeeCode': employee_id}
        out= {}

        try:
            results=collection.find_one(query,{"_id": 1} )   #only id
            emp_id=results["_id"]
        except Exception as e:
            print("MongoDB 1st query failed:", e)

        if results:
            try:
                query2 = {'oReportingToManagerId': emp_id}  #emp_id represents reporting manager's id, we are finding all employees who report to this manager
                result = list(collection.find(
                    query2,
                    {
                        "cEmployeeCode": 1 ,
                        "_id": 0,
                        "obBasicInformation.cFirstName":1,
                        "obBasicInformation.oDesignationId":1
                    }  
                ))
                
                for doc in result:
                    for key, value in doc.items():
                        if key == "obBasicInformation":
                            for k, v in value.items():
                                if k == "oDesignationId":
                                    
                                    # fetch designation
                                    collection = db["hrms_mast_designations"]
                                    des = collection.find_one({'_id': v})
                                    
                                    if des:
                                        value[k] = {
                                            'cDesignationName': des.get('cDesignationName'),
                                            'cDesignationShortName': des.get('cDesignationShortName')
                                        }
            
            except Exception as e:
                print("MongoDB 2nd query failed:", e)
                result = []

            out["reportees"] = result
        
        with open(file_path, "w") as f:
            json.dump(out, f, indent=4)

    return out

# ✅ CORRECT for your ADK version
reportee_tool = FunctionTool(get_reportee_info)
