import os
import io
import subprocess
import platform
import webbrowser
from flask import Flask, request, send_file, send_from_directory

app = Flask(__name__)
UPLOAD_FOLDER = '.' 

# Automatically use the correct Ghostscript command based on your Operating System
GS_COMMAND = r"C:\Program Files\gs\gs10.07.1\bin\gswin64c.exe"

@app.route('/')
def serve_html():
    return send_from_directory('.', 'index.html')

@app.route('/compress-pdf', methods=['POST'])
def compress_pdf():
    if 'file' not in request.files:
        return "No file uploaded", 400
        
    file = request.files['file']
    quality = int(request.form.get('quality', 80))
    
    input_path = os.path.join(UPLOAD_FOLDER, f"temp_{file.filename}")
    output_path = os.path.join(UPLOAD_FOLDER, f"compressed_{file.filename}")
    
    file.save(input_path)

    if quality < 40:
        pdf_setting = "/screen"  
    elif quality < 80:
        pdf_setting = "/ebook"   
    else:
        pdf_setting = "/printer" 
        
    gs_cmd = [
        GS_COMMAND, "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={pdf_setting}", "-dNOPAUSE", "-dQUIET", "-dBATCH",
        f"-sOutputFile={output_path}", input_path
    ]
    
    try:
        subprocess.run(gs_cmd, check=True)
        
        # Read the compressed file into memory so we can delete the file from the disk
        with open(output_path, 'rb') as f:
            return_data = io.BytesIO(f.read())
            
        return send_file(
            return_data, 
            as_attachment=True, 
            download_name=f"compressed_{file.filename}",
            mimetype='application/pdf'
        )
        
    except subprocess.CalledProcessError as e:
        print(f"Ghostscript Error: {e}")
        return "Compression failed. Check if Ghostscript is installed properly.", 500
        
    finally:
        # Always clean up the temporary files
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

if __name__ == '__main__':
    print("Starting local file compressor...")
    webbrowser.open("http://127.0.0.1:5000")
    app.run(port=5000)
