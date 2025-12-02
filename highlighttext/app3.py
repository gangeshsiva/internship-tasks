#cant highlight text in a pdf using pdfplumber

import fitz  # PyMuPDF
import re
import os
import json
import sys
from flask import Flask, request, jsonify
from datetime import datetime
import pdfplumber
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from pytesseract import Output

app=Flask(__name__)

os.makedirs('input',exist_ok=True)
os.makedirs('output',exist_ok=True)
os.makedirs('logs',exist_ok=True)
os.makedirs('jsonoutput',exist_ok=True)

#logging the error
def log_exception(e, func_name, logfile):
    try:
        exc_type, exc_obj, tb = sys.exc_info()
        lineno = tb.tb_lineno if tb else "N/A"
        error_message = f"\n[{datetime.now()}] In {func_name} LINE.NO-{lineno} : {exc_obj} error {e}"
        print(error_message)
        with open(logfile, 'a', encoding='utf-8') as fp:
            fp.writelines(error_message + "\n")
    except Exception as ee:
        print("Logging failed:", ee)


with open('config.json','r') as f:
    config_data=json.load(f)

input_pdf=config_data["input_directory"]
output_pdf=config_data["output_directory"]
pattern=config_data["pattern"]
os.environ['TESSDATA_PREFIX'] = config_data["tessdata"]
pytesseract.pytesseract.tesseract_cmd = config_data["tesseract_exepath"]
popplerpath=config_data["popplerpath"]


#extract_pdf is connected to highlight_pdf (we are sending the icd codes to highlight and only using the fitz in highlighting)
def extract_pdf(input_pdf_path, output_pdf_path, pattern,logpath,jsonpath,library):
    
    regex = re.compile(pattern)
    results=[] 

    if library == "fitz":
        try:
            doc = fitz.open(input_pdf_path)

            for page_num,page in enumerate(doc,start=1):
                page_text = page.get_text("text")
                matches = regex.findall(page_text)  # Only captures the code
                words = page.get_text('words')
                
                word_coords= []

                for w in words:
                    word_coords.append({
                        "text": w[4],
                        "x0": w[0],
                        "y0": w[1],
                        "x1": w[2],
                        "y1": w[3]
                    })

                page_output={
                    "page" : page_num,
                    "codes": matches,
                    "coords" : word_coords
                }

                results.append(page_output)

            highlight_pdf(input_pdf_path, output_pdf_path,logpath,results)
            
            doc.close()
                
        except Exception as e:
            log_exception(e,"extract_pdf using fitz",logpath)
    
    elif library == "pdfplumber":
        try:
            with pdfplumber.open(input_pdf_path) as pdf:
                 for page_num,page in enumerate(pdf.pages,start=1):
                            page_text=page.extract_text()
                            matches = regex.findall(page_text)
                            words = page.extract_words()

                            word_coords= []

                            for w in words:
                                word_coords.append({
                                    "text": w["text"],
                                    "x0": w["x0"],
                                    "y0": w["top"],
                                    "x1": w["x1"],
                                    "y1": w["bottom"]
                                })
                            
                            page_output={
                                    "page" : page_num,
                                    "codes": matches,
                                    "coords" : word_coords
                                }
                            
                            results.append(page_output)
            
            highlight_pdf(input_pdf_path, output_pdf_path,logpath,results)

            pdf.close()
        
        except Exception as e:
            log_exception(e,"extract_pdf using pdfplumber",logpath)

    elif library =="pytesseract":
        try:
            pages = convert_from_path(input_pdf_path, poppler_path=popplerpath)   #converts the pages into a set of images

            for page_num, page in enumerate(pages,start=1):
                page_text=pytesseract.image_to_string(page,lang='eng')
                matches = regex.findall(page_text)  # Only captures the code
                words = pytesseract.image_to_data(page, lang='eng', output_type=Output.DICT)   #gives out a dictionary and not a list
                word_coords= []

                for i in range(len(words["text"])):
                    if words["text"][i].strip() != "":
                        word_coords.append({
                            "text": words["text"][i],
                            "x0": words["left"][i],
                            "y0": words["top"][i],
                            "x1": words["left"][i] + words["width"][i],
                            "y1": words["top"][i] + words["height"][i]
                        })
                
                page_output={
                        "page" : page_num,
                        "codes": matches,
                        "coords" : word_coords
                    }
                
                results.append(page_output)
    
            highlight_pdf(input_pdf_path, output_pdf_path,logpath,results)
       
        except Exception as e:
            log_exception(e,"extract_pdf using pdfplumber",logpath)

    with open(jsonpath, "w") as g:
        json.dump(results, g ,indent=4)

def highlight_pdf(input_pdf_path, output_pdf_path,logpath,results):

    try:
        hdoc = fitz.open(input_pdf_path)

        for page_num, page in enumerate(hdoc, start=1):
            # Loop through results to find the matching page
            page_result = None
            for r in results:
                if r['page'] == page_num:
                    page_result = r
                    break  # stop once the correct page is found
            
            if not page_result:
                continue  # skip if no codes found for this page

            for matched_text in page_result['codes']:
                matched_text = matched_text.strip()
                if matched_text:
                    # search_for returns list of rectangles for the text
                    text_instances = page.search_for(matched_text)
                    for inst in text_instances:
                        highlight = page.add_highlight_annot(inst)
                        highlight.update()

        hdoc.save(output_pdf_path)
        hdoc.close()

    except Exception as e:
        log_exception(e, "highlight_pdf using fitz", logpath)


@app.route('/',methods=["POST","GET"])
def main_route():
    try:
        datas=request.get_json()
        pdfname=datas['filename']
        library=datas.get('library','')
        print(pdfname)
        
        if not library:
            library='fitz'

        logfilename=pdfname.split('.')[0]+".txt"
        logpath=os.path.join('logs',logfilename)
        jsonfilename=pdfname.split('.')[0]+".json"
        jsonpath=os.path.join('jsonoutput',jsonfilename)

        print(datas)
        
        input_pdf_path=os.path.join(input_pdf,pdfname)

        if not pdfname or not pdfname.lower().endswith('.pdf'):
            log_exception(Exception("file unsupported or filename not given"),"main_route",logpath)
            return "error"

        
        if not os.path.exists(input_pdf_path):
            log_exception(Exception("file not found in system"),"main_route",logpath)
            return "error"
        
        output_pdf_path=os.path.join(output_pdf,pdfname)
        print(output_pdf_path)
        # Run the function
        extract_pdf(input_pdf_path, output_pdf_path, pattern,logpath,jsonpath,library)
        return output_pdf_path

    except Exception as e:
        log_exception(e,"main_route",logpath)

if __name__== "__main__" :
    app.run()
