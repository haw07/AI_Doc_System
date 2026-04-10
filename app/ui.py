import streamlit as st
import requests
import json

# Setup Page
st.set_page_config(page_title="CMI Document Reader", page_icon="📄")
st.title("Financial Document Reader")
st.markdown("Upload a Term Sheet, PDF, or Chat Log to extract entities.")

# File Uploader
uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'docx', 'txt'])

if uploaded_file is not None:
    if st.button("Process Document"):
        with st.spinner("AI is analyzing the document..."):
            # Prepare file for the FastAPI endpoint
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            
            try:
                # Call your LOCAL FastAPI server
                response = requests.post("http://127.0.0.1:8000/document/process", files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    st.success("Extraction Complete!")
                    
                    # Layout: Preview and Entities
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Text Preview")
                        st.info(data["text_preview"] + "...")
                        
                    with col2:
                        st.subheader("Extracted Entities")
                        # Display results in a clean table
                        st.table(data["entities"])
                        
                    # Also show raw JSON for developers
                    with st.expander("View Raw JSON"):
                        st.json(data["entities"])
                        
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Could not connect to FastAPI server. Is it running? Error: {e}")