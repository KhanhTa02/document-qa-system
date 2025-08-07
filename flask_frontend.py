from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import logging
import glob
from rag_backend import DocumentQASystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
qa_system = None

def get_first_pdf():
    source_dir = "source_documents"
    if not os.path.exists(source_dir):
        logger.error(f"Source documents directory not found: {source_dir}")
        return None
    
    pdf_files = glob.glob(os.path.join(source_dir, "*.pdf"))
    if not pdf_files:
        logger.error(f"No PDF files found in {source_dir}")
        return None
    
    pdf_path = pdf_files[0]
    logger.info(f"Found PDF: {pdf_path}")
    return pdf_path

def init_qa_system():
    global qa_system
    pdf_path = get_first_pdf()
    
    if not pdf_path:
        logger.error("No PDF file found in source_documents folder")
        return False
    
    try:
        logger.info("Initializing QA system...")
        qa_system = DocumentQASystem(pdf_path)
        logger.info("QA system ready")
        return True
    except Exception as e:
        logger.error(f"QA system init failed: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'success': False, 'error': 'No question provided'}), 400
        
        if qa_system is None:
            return jsonify({'success': False, 'error': 'QA system not ready'}), 500
        
        result = qa_system.answer_question(question)
        
        return jsonify({
            'success': True,
            'answer': result['answer'],
            'sources': result['sources']
        })
        
    except Exception as e:
        logger.error(f"Question processing error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/pdf/<filename>')
def serve_pdf(filename):
    return send_from_directory('source_documents', filename)

@app.route('/api/pdf_info')
def pdf_info():
    pdf_path = get_first_pdf()
    if pdf_path and os.path.exists(pdf_path):
        return jsonify({
            'file_name': os.path.basename(pdf_path),
            'file_path': pdf_path
        })
    return jsonify({'error': 'No PDF file found'}), 404

if __name__ == '__main__':
    if init_qa_system():
        app.run(debug=True, host='0.0.0.0', port=5001)
    else:
        logger.error("Failed to initialize QA system. Exiting.") 