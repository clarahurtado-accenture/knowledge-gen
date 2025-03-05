import streamlit as st
from pathlib import Path
import os
import uuid
from streamlit_quill import st_quill

def save_uploaded_file(uploaded_file):
    """Guarda el archivo subido en una carpeta temporal y devuelve su contenido."""
    file_id = str(uuid.uuid4())
    file_path = f"temp/{file_id}_{uploaded_file.name}"
    os.makedirs("temp", exist_ok=True)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return file_id, file_path, content

def main():
    st.title("Drag & Drop de Documentos con Editor de Texto")
    uploaded_files = st.file_uploader("Arrastra y suelta tus documentos aquí", type=["txt"], accept_multiple_files=True)
    
    if "documents" not in st.session_state:
        st.session_state.documents = {}
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_id, file_path, content = save_uploaded_file(uploaded_file)
            st.session_state.documents[file_id] = {"name": uploaded_file.name, "content": content}
    
    for file_id, doc in st.session_state.documents.items():
        st.subheader(f"Editando: {doc['name']}")
        doc["content"] = st_quill(value=doc["content"], key=file_id)
        
        if st.button(f"Guardar cambios - {doc['name']}", key=f"save_{file_id}"):
            with open(f"temp/{file_id}_{doc['name']}", "w", encoding="utf-8") as f:
                f.write(doc["content"])
            st.success(f"Documento {doc['name']} guardado exitosamente")

if __name__ == "__main__":
    main()
