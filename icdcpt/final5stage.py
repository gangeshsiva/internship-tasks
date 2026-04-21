import json, re
from datetime import datetime
import os, sys, json, requests
import datefinder
from fuzzywuzzy import fuzz
import tiktoken

with open('config.json', 'r') as f:
    config_data = json.load(f)

cptjsonpath=config_data["cptjsonpath"] 
icdjsonpath=config_data["icdjsonpath"]
sctjsonpath=config_data["sctjsonpath"]
#logfile=config_data["logfile"]
#inputjsonpath=config_data["inputjsonpath"]
#outputjsonpath=config_data["outputjsonpath"]

def log_exception(e, func_name, logfile):
    exc_type, exc_obj, tb = sys.exc_info()
    lineno = tb.tb_lineno
    error_message = f"\nIn {func_name} LINE.NO-{lineno} : {exc_obj}"
    print("error_message : ", error_message)
    with open(logfile, 'a', encoding='utf-8') as fp:
        fp.writelines(error_message)

headers = {
    "Content-Type": "application/json",
}

def ICDsqlEndpoint(labData, DocumentID, SQlurl, env, logfile):
    try:
        # url = config_data['sqlendpoint']

        # print('DocumentID : ',DocumentID)
        # payload = {"documentDetailId":DocumentID,"data":json.dumps(medData)}
        payload = json.dumps(labData)
        # print('DocumentID : ',DocumentID)
        # print('ApiKey : ',data['StageApiKey'])
        if env.lower() == "stage":
            # print('stage')
            stagebaseURL = config_data["stageBaseURL"]
            stageICDController = config_data["ICDCPTController"]
            url = stagebaseURL + stageICDController
            # url = config_data['sqlendpoint']
            url = url.replace(url[-1], str(DocumentID))
            print('stage url Labs : ', url)
            headers = {
                'ApiKey': config_data['stageApiKey'],
                'Content-Type': 'application/json'
            }
        else:
            # print('prod')
            prodbaseURL = config_data["prodBaseURL"]
            prodICDController = config_data["ICDCPTController"]
            url = prodbaseURL + prodICDController
            url = url.replace(url[-1], str(DocumentID))
            headers = {
                'ApiKey': config_data['prodApiKey'],
                'Content-Type': 'application/json'
            }
            print('production url Labs : ', url)
            # print('production url Labs : ',config_data['LabProdsqlendpoint'])
            # print(config_data['ProductionAPIKey'])
        response = requests.request("POST", url, headers=headers, data=payload)
        return response
    except Exception as e:
        log_exception(e, "ICDsqlEndpoint", logfile)


def remove_duplicates(data):
    try:
        seen = set()
        unique_list = []

        for item in data:
            # Convert dictionary (including nested dictionaries) into a JSON string (hashable format)
            item_str = json.dumps(item, sort_keys=True)
            if item_str not in seen:
                seen.add(item_str)
                unique_list.append(item)

        return unique_list
    except Exception as e:
        return data


def check_match_words(word, page_num, word_coordinates,isFuzz, logfile):
    try:
        reg = r'[^A-Za-z0-9]'
        word_list = []
        isTrue = False
        for i, coordinate in enumerate(word_coordinates):
            if isFuzz:
                re_word = re.sub(reg, "", word.lower())
                if coordinate["text"]:
                    re_text = re.sub(reg, "", coordinate["text"].lower())
                    isTrue = fuzz.partial_ratio(re_text, re_word) > 90
            else:
                isTrue = re.sub(reg, "", coordinate["text"].lower()) == re.sub(reg, "", word.lower())

            if isTrue:
                if bool(re.search(re.sub(reg, "", word.lower()), re.sub(reg, "", coordinate["text"].lower()))):
                    word_list.append({
                        'x0': coordinate["x0"],
                        'y0': coordinate["y0"],
                        'x1': coordinate["x1"],
                        'y1': coordinate["y1"],
                        'height': coordinate["height"],
                        'width': coordinate["width"],
                        'page_num': coordinate["Page"],
                    })

        return word_list
    except Exception as e:
        log_exception(e, "check_match_words", logfile)
        return []


def check_match_coordinates(word_list, check_word_coord, page_num, logfile):
    try:
        data = {}
        if word_list:
            # REMOVE DUP
            seen = set()
            non_dup = []
            for non_data in word_list:
                key = (non_data["x0"], non_data['y0'], non_data["x1"], non_data['y1'], non_data['height'],
                       non_data['width'], non_data['page_num'])
                if not key in seen:
                    seen.add(key)
                    non_dup.append(non_data)
                    # print(non_dup)
            if check_word_coord:
                if not check_word_coord["y0"] == 0:
                    check_coord = []
                    for coord in non_dup:
                        if check_word_coord["y0"] < coord["y0"]:
                            check_coord.append(coord)
                            break
                    if check_coord:
                        data = {
                            'x0': check_coord[0]["x0"],
                            'x1': check_coord[0]["x1"],
                            'y0': check_coord[0]["y0"],
                            'y1': check_coord[0]["y1"],
                            'height': check_coord[0]["height"],
                            'width': check_coord[0]["width"],
                            'page_num': check_coord[0]["page_num"]
                        }
                    else:
                        data = {
                            'x0': 0,
                            'x1': 0,
                            'y0': 0,
                            'y1': 0,
                            'height': 0,
                            'width': 0,
                            'page_num': page_num,
                        }
                else:
                    data = {
                        'x0': non_dup[0]["x0"],
                        'x1': non_dup[0]["x1"],
                        'y0': non_dup[0]["y0"],
                        'y1': non_dup[0]["y1"],
                        'height': non_dup[0]["height"],
                        'width': non_dup[0]["width"],
                        'page_num': non_dup[0]["page_num"]
                    }
            else:

                data = {
                    'x0': non_dup[0]["x0"],
                    'x1': non_dup[0]["x1"],
                    'y0': non_dup[0]["y0"],
                    'y1': non_dup[0]["y1"],
                    'height': non_dup[0]["height"],
                    'width': non_dup[0]["width"],
                    'page_num': non_dup[0]["page_num"]
                }
        else:
            data = {
                'x0': 0,
                'x1': 0,
                'y0': 0,
                'y1': 0,
                'height': 0,
                'width': 0,
                'page_num': page_num,
            }

        return data

    except Exception as e:
        log_exception(e, "check_match_coordinates", logfile)
        return {}


def default_coordinates():
    return {'x0': 0, 'y0': 0, 'x1': 0, 'y1': 0, 'height': 0, 'width': 0}


def match_coordinates(output, word_coordinates, logfile):
    try:
        new_data = []
        reg = r'[^A-Za-z0-9]'
        for data in output:
            # CODE
            page_num = data["Page"]

            if data["codeType"] == "ICD10" or data["codeType"] == "CPT":
                word_list = check_match_words(data["code"], page_num, word_coordinates[page_num - 1], True, logfile)

            elif data["codeType"] == "SCT":
                word_list = check_match_words(data["ConceptId"], page_num, word_coordinates[page_num - 1], False, logfile)

            fin_coord = check_match_coordinates(word_list, {}, page_num, logfile)
            data["code_coordinates"] = fin_coord
            # DESC
            page_num = data["Page"]
            word_list = check_match_words(data["description"], page_num, word_coordinates[page_num - 1], True, logfile)
            fin_coord = check_match_coordinates(word_list, {}, page_num, logfile)
            data["description_coordinates"] = fin_coord
            new_data.append(data)
        return new_data
    except Exception as e:
        log_exception(e, "match_coordinates", logfile)
        return output

Date_extraction_instructions= """
You are an expert date extraction system.

Your task is to extract a single relevant medical date from the given context and normalize it to the format "YYYY-MM-DD"

Include ONLY the following types of dates:
Visit Date
DOS (Date of Service)
Doctor Service Date
Encounter Date (including variations like "date of encounter", "encounter on", etc.)
Performed Date
Electronically Signed Date

Exclude the following:
Date of Birth (DOB) or any birth-related dates
Any unrelated administrative or non-medical dates

Instructions:
Identify dates even if they appear in different formats (e.g., MM/DD/YYYY, DD-MM-YYYY, Month DD, YYYY, etc.)
If multiple valid dates are present, select the most relevant encounter-related date (prefer Visit/Encounter/Service date over others; if not available, use Performed or Electronically Signed date)
If no relevant date is found, return "1900-01-01" as a default value.
Convert the selected date into YYYY-MM-DD format

Output Format:
Return ONLY a single string:

"YYYY-MM-DD"
"""

def vertexAI_endpoint(context, context_length, SYSTEM_PROMPT=Date_extraction_instructions,logfile=config_data["logfile"]):
    try:
        url = config_data["vertexAI_url"]  # GET FROM CONFIG

        payload = json.dumps({
            "context": context,
            "context_length": context_length,
            "SYSTEM_PROMPT": SYSTEM_PROMPT
        })

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, data=payload, timeout=120)
        print(type(response))
        print(response.text)

        # ---------------------------
        # Step 1: Get raw text safely
        # ---------------------------
        try:
            raw_output = response.json().get("result", "")
        except Exception:
            raw_output = response.text

        return raw_output.strip()
    
    except Exception as e:
        log_exception(e, "vertexAI_endpoint", logfile)
        return "1900-01-01"

def token_length(context, SYSTEM_PROMPT=Date_extraction_instructions):    
    encoding = tiktoken.get_encoding("cl100k_base")

    tokens = encoding.encode(context+SYSTEM_PROMPT)
    tokenlength =  len(tokens)
    buffer = 200
    if tokenlength>4096+buffer:
        context_length=8192
    elif tokenlength>2048+buffer:
        context_length=4096
    elif tokenlength>1024+buffer:
        context_length=2048
    elif tokenlength>512+buffer:
        context_length=1024
    elif tokenlength>256+buffer:
        context_length=512
    else:
        context_length=256
    
    return context_length

def ICD_CPT_SCT_code(all_text, words_coordinates,documentDetailId,environment, logfile):
    try:
        with open(icdjsonpath, 'r') as f:
            ICD10jsondata = json.load(f)

        with open(cptjsonpath, 'r') as f:
            CPTjsondata = json.load(f)

        with open(sctjsonpath, 'r') as f:
            SCTjsondata = json.load(f)

    except Exception as e:
        log_exception(e, "File Reading", logfile)
        print("Error in reading the json files that contain all the icd codes, cpt codes and snowmed codes.")

    ICDfilteredjson={}
    CPTfilteredjson={}
    Snomedfilteredjson={}

    for data in ICD10jsondata['mastICD10CM']:
        ICDfilteredjson[data['cICD_10_Code']] = data['cShort_Description']

    for data in CPTjsondata['mastCPT']:
        CPTfilteredjson[data['Code']] = data['Description']

    for data in SCTjsondata['mastSnowMedCodes']:
        Snomedfilteredjson[data['Code']] = data
        Snomedfilteredjson[data['ConceptId']] = data

    ICDpattern=r"\b(?<!\d{2})(?<!\d{2}[ ])(?<!mo\s)(?<!A:\s)(?<!-)(?<!BMI:\s)[A-Z0-9]{1,4}[.,][A-Z0-9]{1,4}\b(?!\s*(?:AM|PM|am|pm|m2|kg|F|/h|years|PST|PDT|\.|Ibs|cm|T|Fo|C|bpm|mL|mg|-|Wt|in|/|%|\(lbs\)))"   #(?:ICD[-\s]*10\s*)?
    ICDpattern2=r"\b(?<!\d{2})(?<!\d{2}[ ])(?<!mo\s)(?<!A:\s)(?<!-)(?<!BMI:\s)[A-Z][0-9]{2}\b(?!\s*(?:AM|PM|am|pm|m2|kg|F|/h|years|PST|PDT|\.|Ibs|cm|T|Fo|C|bpm|mL|mg|-|Wt|in|/|%|\(lbs\)))"
    ICDpattern3=r"\b(?<!\d{2})(?<!\d{2}[ ])(?<!mo\s)(?<!A:\s)(?<![-#])(?<![A-Z][ ])(?<!BMI:\s)[A-Z0-9]{4,7}\b(?!\s*(?:AM|PM|am|pm|m2|kg|F|/h|years|PST|PDT|\.|Ibs|cm|T|Fo|C|bpm|mL|mg|-|Wt|in|/|%|[A-Z]{2}|[A-Z][ ]|\(lbs\)))"

    state_codes = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]
    state_pattern = "|".join(state_codes)
    
    CPTpattern=rf"\b(?<!\b(?:{state_pattern})\s)(?<!MRN:\s)(?<![/])(?<!\d{{2}})(?<!\d{{2}}[ ])(?<!\.)(?<!#\s)(?:(?<=PC-)|(?<!\w))\d{{5}}\b(?!\s*(?:-|/|\.))"

    SCTpattern=r"(?:(?<=SCT\s)|(?<=Code:\s)|(?<=SNOMED:)|(?<=SNOMED\s))\b[0-9]{6,18}\b"
 
    #DOB = '1900-01-01'     ##
    #date_pattern = r'\d{1,2}/\d{1,2}/\d{2,4}'  
    #Date_keywords = ['Performed Date', "electronically signed", "encounter","visit date"]    
    #formatted_date = "1900-01-01"
    codePages = []
    unique_pairs = set()
    all_data = []

    try:
        for page_num, text in enumerate(all_text, start=1):

            icdmatch=re.findall(ICDpattern,text, re.IGNORECASE)
            icdmatch2=re.findall(ICDpattern2,text)
            icdmatch3=re.findall(ICDpattern3,text)

            cptmatch=re.findall(CPTpattern,text, re.IGNORECASE)
            sctmatch=re.findall(SCTpattern,text)
            context_length = token_length(text)
            # for date_key in Date_keywords:
            #     date_match_text = re.search(date_key, text, re.IGNORECASE)
            #     if date_match_text:
            #         date_text = text[date_match_text.end():]
            #         text_date = re.search(date_pattern, date_text, re.IGNORECASE)

            #         if text_date:
            #             formatted_date = Accurate_date(str(text_date.group()), logfile)
            #             break

            if icdmatch:
                ICDPagenum = page_num - 1

                corrected_icd = []

                first_letter_map = {
                    '1': 'I', 'l': 'I',
                    '2': 'Z', 'z': 'Z',                           #FIRST PART CHANGE 1,l --> I , 2,z --> Z , 8 --> B , 5,s --> S , o,0 --> O  
                    '8': 'B',
                    '5': 'S', 's': 'S',
                    'o': 'O', '0': 'O'
                }

                after_first_map = {
                    'O': '0', 'o': '0',
                    'I': '1', 'l': '1',                           #SECOND PART CHANGE O,o --> 0 , I,l --> 1 , S,s -->5 , B --> 8 , Z,z --> 2
                    'S': '5', 's': '5',    
                    'B': '8',
                    'Z': '2', 'z': '2'
                }

                for item in icdmatch:
                    if not item:
                        continue

                    # Fix first character
                    if len(item) > 3 and item[3] == '.':
                        first_char = first_letter_map.get(item[0], item[0])
                    
                        # Fix remaining characters
                        rest = ''.join(after_first_map.get(c, c) for c in item[1:])
                    
                        corrected_icd.append(first_char + rest)

                    elif len(item) > 3 and item[3] == ',' :
                        first_char = first_letter_map.get(item[0], item[0])
                    
                        # Fix remaining characters
                        rest = ''.join(after_first_map.get(c, c) for c in item[1:])
                        
                        
                        corrected_icd.append(first_char + rest[:2] + '.' + rest[3:])

                for icd in corrected_icd:
                    if icd in ICDfilteredjson:
                        ICD_data = {
                                "Page": page_num,
                                "code": icd,
                                "description": ICDfilteredjson[icd],
                                "codeType": "ICD10"
                            }
                        print(ICD_data)

                        if ICDPagenum not in codePages:
                            codePages.append(ICDPagenum)
                            ICD_data['date'] = vertexAI_endpoint(text , context_length = context_length)
                            pair = ( ICD_data["date"], ICDPagenum)
                            unique_pairs.add(pair)
                        else:
                            for date, page in unique_pairs:
                                if page == ICDPagenum:
                                    ICD_data['date'] = date
                                    break
                                
                        all_data.append(ICD_data)
            
            if icdmatch2:
                ICDPagenum = page_num - 1

                for icd in icdmatch2:
                    if icd in ICDfilteredjson:
                        ICD_data = {
                                "Page": page_num,
                                "code": icd,
                                "description": ICDfilteredjson[icd],
                                "codeType": "ICD10"
                            }
                        
                        
                        if ICDPagenum not in codePages:
                            codePages.append(ICDPagenum)
                            ICD_data['date'] = vertexAI_endpoint(text , context_length = context_length)
                            pair = ( ICD_data["date"], ICDPagenum)
                            unique_pairs.add(pair)
                        else:
                            for date, page in unique_pairs:
                                if page == ICDPagenum:
                                    ICD_data['date'] = date
                                    break

                        all_data.append(ICD_data)

            if icdmatch3:
                ICDPagenum = page_num - 1

                corrected_icd=[]

                for item in icdmatch3:
                    if not item:
                        continue

                    elif item.isdigit() and len(item) == 4 and int(item)>1950 and int(item)<2100 :
                        continue

                    elif item.isalpha():
                        continue

                    # Fix first character
                    else:
                        first_char = first_letter_map.get(item[0], item[0])
                    
                        # Fix remaining characters
                        rest = ''.join(after_first_map.get(c, c) for c in item[1:])
                    
                        corrected_icd.append(first_char + rest[0:2] + '.' + rest[2:])


                for icd in corrected_icd:
                    if icd in ICDfilteredjson:
                        ICD_data = {
                                "Page": page_num,
                                "code": icd,
                                "description": ICDfilteredjson[icd],
                                "codeType": "ICD10"
                            }

                        if ICDPagenum not in codePages:
                            codePages.append(ICDPagenum)
                            ICD_data['date'] = vertexAI_endpoint(text , context_length = context_length)
                            pair = ( ICD_data["date"], ICDPagenum)
                            unique_pairs.add(pair)
                        else:
                            for date, page in unique_pairs:
                                if page == ICDPagenum:
                                    ICD_data['date'] = date
                                    break

                        all_data.append(ICD_data)                            

            if cptmatch:
                CPTPagenum = page_num - 1

                for cpt in cptmatch:
                    if cpt.isdigit() and len(cpt) == 5 and cpt in CPTfilteredjson:
                        CPT_data = {
                                "Page": page_num,
                                "code": cpt,
                                "description": CPTfilteredjson[cpt],
                                "codeType": "CPT"
                            }

                        if CPTPagenum not in codePages:
                            codePages.append(CPTPagenum)
                            CPT_data['date'] = vertexAI_endpoint(text , context_length = context_length)
                            pair = ( CPT_data["date"], CPTPagenum)
                            unique_pairs.add(pair)
                        else:
                            for date, page in unique_pairs:
                                if page == CPTPagenum:
                                    CPT_data['date'] = date
                                    break

                        all_data.append(CPT_data)

            if sctmatch:
                SCTPagenum = page_num - 1

                for sct in sctmatch:
                    for c,v in Snomedfilteredjson.items():
                        if sct.isdigit() and 6 <= len(sct) <= 18 and sct==c:
                            SCT_data = {
                                    "codeType" : "SCT",
                                    "Page" : page_num,
                                    "code" : v["Code"], 
                                    "description" : v["Description"],
                                    "ConceptId" :v["ConceptId"],
                                }

                            if SCTPagenum not in codePages:
                                codePages.append(SCTPagenum)
                                SCT_data['date'] = vertexAI_endpoint(text , context_length = context_length)
                                pair = ( SCT_data["date"], SCTPagenum)
                                unique_pairs.add(pair)
                            else:
                                for date, page in unique_pairs:
                                    if page == SCTPagenum:
                                        SCT_data['date'] = date
                                        break
                        
                            all_data.append(SCT_data)                            
                            

        data_with_cordinates = match_coordinates(all_data, words_coordinates, logfile)
        data_with_cordinates = remove_duplicates(data_with_cordinates)
        #print(data_with_cordinates)
        
        print(f"data_with_cordinates {type(data_with_cordinates)} ,{len(data_with_cordinates)}")
        SQlurl = ''
        ICDresponse = ICDsqlEndpoint(data_with_cordinates, documentDetailId, SQlurl, environment, logfile)
        print('ICD SQL response : ', ICDresponse)
        
        
        return data_with_cordinates

    except Exception as e:
        log_exception(e, "ICD_CPT_code", logfile)      

