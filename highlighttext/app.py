import fitz  # PyMuPDF
import re
import os
import json
import sys
from flask import Flask, request, jsonify

#input_pdf_path = r"C:\Users\gangeshvar.s\Desktop\highlighttext\input\AI_11_ISC_2 1.pdf"
#output_pdf_path = r"C:\Users\gangeshvar.s\Desktop\highlighttext\output\AI_11_ISC_2 1.pdf"

# Match 'CM:' literally, then capture the ICD code
#pattern = r'CM:\s*([A-Z0-9]+\.[0-9]+|[A-Z0-9]+)'
# os.makedirs(logf,exist_ok=True)
os.makedirs('input',exist_ok=True)
os.makedirs('output',exist_ok=True)

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


output_pdf_path=os.path.join(output_pdf,"AI_11_ISC_2 1.pdf")

def highlight_regex_in_pdf(input_pdf_path, output_pdf_path, pattern):
    doc = fitz.open(input_pdf_path)
    regex = re.compile(pattern)

    for page in doc:
        page_text = page.get_text("text")
        matches = regex.findall(page_text)  # Only captures the code
        for matched_text in matches:
            matched_text = matched_text.strip()
            if matched_text:
                text_instances = page.search_for(matched_text)
                for inst in text_instances:
                    highlight = page.add_highlight_annot(inst)
                    highlight.update()

    doc.save(output_pdf_path)
    doc.close()
    print(f"Highlighted PDF saved as: {output_pdf_path}")
   
app=Flask(__name__)

@app.route('/',methods=["POST"])
def main_route():
    try:
        datas=request.get_json()
        pdfname=datas['filename']

        if not pdfname or not pdfname.lower().endswith('.pdf'):
            log_exception("file unsupported or not found","main_route",log.txt)
            return error

        input_pdf_path=os.path.join(input_pdf,pdfname+'.pdf')
        
        if not os.path.exists(input_pdf_path):
            log_exception()

# Run the function
highlight_regex_in_pdf(input_pdf_path, output_pdf_path, pattern)

