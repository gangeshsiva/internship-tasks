import fitz  # PyMuPDF
import re
import os
import json
import sys
from flask import Flask, request, jsonify
from datetime import datetime

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


def extract_and_highlight_pdf(input_pdf_path, output_pdf_path, pattern,logpath,jsonpath):
    try:
        doc = fitz.open(input_pdf_path)
        regex = re.compile(pattern)

        results=[]

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


            for matched_text in matches:
                matched_text = matched_text.strip()
                if matched_text:
                    text_instances = page.search_for(matched_text)
                    for inst in text_instances:
                        highlight = page.add_highlight_annot(inst)
                        highlight.update()

        doc.save(output_pdf_path)
        doc.close()
        

        with open(jsonpath, "w") as g:
            json.dump(results, g ,indent=4)
        

    except Exception as e:
        log_exception(e,"highlight_regex_in_pdf",logpath)




@app.route('/',methods=["POST","GET"])
def main_route():
    try:
        datas=request.get_json()
        pdfname=datas['filename']
        print(pdfname)
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
        extract_and_highlight_pdf(input_pdf_path, output_pdf_path, pattern,logpath,jsonpath)
        return output_pdf_path

    except Exception as e:
        log_exception(e,"main_route",logpath)

if __name__== "__main__" :
    app.run()