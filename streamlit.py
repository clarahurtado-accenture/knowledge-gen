import streamlit as st
import os
import uuid
from streamlit_quill import st_quill
import PyPDF2
from docx import Document

# Crear carpetas temporales
for folder in ["temp", "temp_edited"]:
    if os.path.exists(folder):
        for file in os.listdir(folder):
            os.remove(os.path.join(folder, file))
    else:
        os.makedirs(folder)

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
