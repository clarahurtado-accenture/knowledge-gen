import streamlit as st
import os
import uuid
import requests
from streamlit_quill import st_quill
import PyPDF2
from docx import Document
from firecrawl import FirecrawlApp

# Crear carpetas temporales
for folder in ["temp", "temp_edited"]:
    if os.path.exists(folder):
        for file in os.listdir(folder):
            os.remove(os.path.join(folder, file))
    else:
        os.makedirs(folder)
# Initialize the Firecrawl client
app = FirecrawlApp(api_key="fc-YOUR_API_KEY")  # Replace with your actual API key

def save_uploaded_file(uploaded_file):
    """Guarda el archivo subido y devuelve su contenido."""
    file_id = str(uuid.uuid4())
    file_path = f"temp/{file_id}_{uploaded_file.name}"
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Leer el contenido del archivo
    content = ""
    if uploaded_file.type == "application/pdf":
        content = extract_pdf_text(file_path)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        content = extract_docx_text(file_path)
    else:
        # Suponer que es un archivo de texto (.txt)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    
    return file_id, file_path, content

# Function to crawl a website and handle pagination
def save_file_from_url(url, limit=100, poll_interval=30):

    # Start the crawl job
    crawl_status = app.crawl_url(
        url,
        params={
            'limit': limit,
            'scrapeOptions': {'formats': ['markdown', 'html']}
        },
        poll_interval=poll_interval
    )
    
    # Check the crawl status and retrieve results
    crawl_id = crawl_status['id']
    all_data = []
    while True:
        status_response = app.check_crawl_status(crawl_id)
        if status_response['status'] == True:
            # Append the current data to the results
            if 'data' in status_response:
                all_data.extend(status_response['data'])
    
            # Check if there is more data to fetch
            if 'next' in status_response:
                crawl_id = status_response['next'].split('/')[-1]  # Extract the new crawl ID from the next URL
            else:
                break
    
    file_extension = url.split('.')[-1].lower()
    file_id = str(uuid.uuid4())
    file_path = f"temp/{file_id}_from_url.{file_extension}"
    
    with open(file_path, "wb") as file:
        for page in all_data:
            file.write(f"Page URL: {page['metadata']['sourceURL']}\n")
            file.write(f"Title: {page['metadata']['title']}\n")
            file.write(f"Description: {page['metadata']['description']}\n")
            file.write(f"Markdown Content:\n{page.get('markdown', 'N/A')}\n")
            file.write(f"HTML Content:\n{page.get('html', 'N/A')}\n")
            file.write("---\n")
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return file_id, file_path, content

def extract_pdf_text(file_path):
    """Extrae el texto de un archivo PDF."""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_docx_text(file_path):
    """Extrae el texto de un archivo DOCX."""
    doc = Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def main():
    st.title("Drag & Drop de Documentos con Editor de Texto")
    
    # Inicializar session_state si no existe
    if "documents" not in st.session_state:
        st.session_state.documents = {}
    
    # Inicializar lista de URLs si no existe
    if "urls" not in st.session_state:
        st.session_state.urls = [""]

# Mostrar los campos de entrada para las URLs
    for i in range(len(st.session_state.urls)):
        url_input = st.text_input(f"Introduce la URL #{i + 1}", value=st.session_state.urls[i], key=f"url_{i}")
        st.session_state.urls[i] = url_input

    # Botón para agregar un nuevo campo de URL
    if st.button("Agregar más URL"):
        st.session_state.urls.append("")

    # Botón para descargar desde las URLs
    if st.button("Descargar desde URLs"):
        for url in st.session_state.urls:
            if url:
                file_id, file_path, content = save_file_from_url(url)
                if file_id:
                    st.session_state.documents[file_id] = {"name": f"Archivo desde {url}", "content": content}


    
    # Subida de archivos con botón de submit
    uploaded_files = st.file_uploader(
        "Arrastra y suelta tus documentos aquí", type=["txt", "pdf", "docx"], accept_multiple_files=True
    )
    
    if st.button("Subir documentos"):
        if uploaded_files:
            for uploaded_file in uploaded_files:
                if uploaded_file.name not in [doc["name"] for doc in st.session_state.documents.values()]:
                    file_id, file_path, content = save_uploaded_file(uploaded_file)
                    st.session_state.documents[file_id] = {"name": uploaded_file.name, "content": content}
    
    # Mostrar editores para cada documento cargado
    for file_id, doc in st.session_state.documents.items():
        st.subheader(f"Editando: {doc['name']}")
        edited_content = st_quill(value=doc["content"], key=f"editor_{file_id}")
        
        if edited_content is not None:
            st.session_state.documents[file_id]["content"] = edited_content
        
        if st.button(f"Guardar {doc['name']}", key=f"save_btn_{file_id}"):
            edited_path = f"temp_edited/{file_id}_{doc['name']}"
            with open(edited_path, "w", encoding="utf-8") as f:
                f.write(edited_content)
            st.success(f"{doc['name']} guardado exitosamente en temp_edited")
    
if __name__ == "__main__":
    main()
