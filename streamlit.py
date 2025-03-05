import streamlit as st
import os
import uuid
from streamlit_quill import st_quill

# Crear carpeta temporal si no existe
os.makedirs("temp", exist_ok=True)

def save_uploaded_file(uploaded_file):
    """Guarda el archivo subido si no está ya en session_state."""
    file_id = str(uuid.uuid4())
    file_path = f"temp/{file_id}_{uploaded_file.name}"

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return file_id, file_path, content

def main():
    st.title("Drag & Drop de Documentos con Editor de Texto")

    # Inicializar session_state
    if "documents" not in st.session_state:
        st.session_state.documents = {}

    # Subida de archivos
    uploaded_files = st.file_uploader(
        "Arrastra y suelta tus documentos aquí", type=["txt"], accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_id = f"{uploaded_file.name}"
            if file_id not in st.session_state.documents:
                file_id, file_path, content = save_uploaded_file(uploaded_file)
                st.session_state.documents[file_id] = {"name": uploaded_file.name, "content": content}

    # Mostrar editores de texto solo para archivos únicos
    to_delete = []
    for file_id, doc in st.session_state.documents.items():
        st.subheader(f"Editando: {doc['name']}")
        edited_content = st_quill(value=doc["content"], key=file_id)

        if st.button(f"Guardar cambios - {doc['name']}", key=f"save_{file_id}"):
            file_path = f"temp/{file_id}"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(edited_content)
            st.success(f"Documento {doc['name']} guardado exitosamente")

    # Eliminar archivos si el usuario lo desea
    if st.button("Limpiar documentos"):
        st.session_state.documents.clear()
        st.experimental_rerun()

if __name__ == "__main__":
    main()
