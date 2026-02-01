"""
Streamlit Document Parser Interface

Simple web interface for document upload and RAG queries.

Author: Junior Developer
Date: 2026-02-01
Version: 1.0.0
"""

import streamlit as st
import requests
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Pyxon AI Document Parser", page_icon="📚", layout="wide")

st.title("📚 Pyxon AI Document Parser")
st.markdown("---")

# Sidebar navigation
page = st.sidebar.radio(
    "Navigation", ["📤 Upload Documents", "🔍 Query Documents", "📊 Document List"]
)

# Page: Upload Documents
if page == "📤 Upload Documents":
    st.header("Upload Documents")

    uploaded_file = st.file_uploader(
        "Choose a document",
        type=["pdf", "docx", "doc", "txt", "png", "jpg", "jpeg"],
        help="Supported formats: PDF, DOCX, DOC, TXT, PNG, JPG, JPEG",
    )

    if uploaded_file and st.button("Process Document"):
        with st.spinner("Processing document..."):
            try:
                # Upload file to API
                files = {
                    "file": (uploaded_file.name, uploaded_file, uploaded_file.type)
                }
                response = requests.post(f"{API_BASE_URL}/parse/upload", files=files)

                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ {result['message']}")
                    st.info(f"**Document ID:** `{result['document_id']}`")
                    st.info(f"**Chunks created:** {result['chunk_count']}")
                else:
                    st.error(f"Error: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error(
                    "⚠️ Cannot connect to API. Make sure the server is running: `uvicorn api.main:app --reload`"
                )
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Page: Query Documents
elif page == "🔍 Query Documents":
    st.header("Query Documents")

    query = st.text_input(
        "Enter your question:", placeholder="What is this document about?"
    )
    top_k = st.slider("Number of results", min_value=1, max_value=10, value=5)

    if query and st.button("Search"):
        with st.spinner("Searching..."):
            try:
                # Query API
                payload = {"query": query, "top_k": top_k}
                response = requests.post(
                    f"{API_BASE_URL}/retrieval/query", json=payload
                )

                if response.status_code == 200:
                    result = response.json()
                    
                    # Display AI Answer
                    answer = result.get("answer")
                    if answer:
                        st.markdown("### 🤖 AI Answer")
                        st.info(answer)
                        st.divider()
                        
                    st.success(f"Found {result['total_results']} relevant chunks")

                    for i, chunk in enumerate(result["chunks"]):
                        score = chunk.get("score", 0)
                        metadata = chunk.get("metadata", {})
                        filename = metadata.get("filename", "Unknown Document")
                        
                        with st.expander(f"📄 {filename} (Score: {score:.3f})"):
                            st.write(chunk["content"])
                            st.caption(
                                f"Source: {filename} | ID: {metadata.get('document_id', 'Unknown')}"
                            )
                else:
                    st.error(f"Error: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("⚠️ Cannot connect to API. Make sure the server is running.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Page: Document List
elif page == "📊 Document List":
    st.header("Processed Documents")
    
    # Initialize session state for documents
    if "documents" not in st.session_state:
        st.session_state.documents = []
    
    # Load documents on page load or refresh
    def load_documents():
        try:
            response = requests.get(f"{API_BASE_URL}/parse/documents")
            if response.status_code == 200:
                st.session_state.documents = response.json().get("documents", [])
                return True
            else:
                st.error(f"Error loading documents: {response.text}")
                return False
        except requests.exceptions.ConnectionError:
            st.error("⚠️ Cannot connect to API. Make sure the server is running.")
            return False
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return False
    
    # Delete document function
    def delete_document(doc_id):
        try:
            response = requests.delete(f"{API_BASE_URL}/parse/documents/{doc_id}")
            if response.status_code == 200:
                st.success(f"✅ Document deleted successfully!")
                # Remove from session state
                st.session_state.documents = [d for d in st.session_state.documents if d.get('id') != doc_id]
                return True
            else:
                st.error(f"Delete failed: {response.text}")
                return False
        except Exception as e:
            st.error(f"Delete error: {str(e)}")
            return False
    
    # Refresh button
    if st.button("🔄 Refresh List"):
        load_documents()
    
    # Auto-load on first visit
    if not st.session_state.documents:
        load_documents()
    
    # Display documents
    if st.session_state.documents:
        st.success(f"Total documents: {len(st.session_state.documents)}")
        
        for doc in st.session_state.documents:
            doc_id = doc.get('id', 'unknown')
            filename = doc.get('filename', 'Unknown')
            
            col1, col2 = st.columns([4, 1])
            
            with col1:
                with st.expander(f"📄 {filename}"):
                    st.write(f"**ID:** `{doc_id}`")
                    st.write(f"**Type:** {doc.get('file_type', 'N/A')}")
                    st.write(f"**Pages:** {doc.get('page_count', 'N/A')}")
                    st.write(f"**Language:** {doc.get('language') or 'Not detected'}")
                    st.write(f"**Uploaded:** {doc.get('upload_date', 'N/A')}")
            
            with col2:
                if st.button("🗑️ Delete", key=f"delete_{doc_id}"):
                    if delete_document(doc_id):
                        st.rerun()
    else:
        st.info("No documents found. Upload some documents to get started!")

# Footer
st.markdown("---")
st.caption("Pyxon AI Document Parser v1.0.0 | Made By Abdelrahman Belal Kanakri")
