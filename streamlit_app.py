import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"

st.title("📄 Insurance RAG Chatbot")

# =====================================================
# SESSION STATE
# =====================================================
if "uploaded_doc_name" not in st.session_state:
    st.session_state.uploaded_doc_name = None

if "doc_id" not in st.session_state:
    st.session_state.doc_id = None

if "refresh_docs" not in st.session_state:
    st.session_state.refresh_docs = True

if "docs" not in st.session_state:
    st.session_state.docs = []


# =====================================================
# FETCH DOCUMENTS (CONTROLLED REFRESH)
# =====================================================
def fetch_documents():
    try:
        print('Invoking fetch_documents ')
        res = requests.get(f"{BASE_URL}/documents/")
        return res.json() if res.status_code == 200 else []
    except:
        return []


if st.session_state.refresh_docs:
    st.session_state.docs = fetch_documents()
    st.session_state.refresh_docs = False

docs = st.session_state.docs
doc_map = {}
print(f'length of documents recieved : {len(docs)}, {type(docs)}')
if len(docs) >0:
    print('inside doc_map creation')
    doc_map = {d["name"]: d["doc_id"] for d in docs}


# =====================================================
# SIDEBAR: UPLOAD ONLY
# =====================================================
st.sidebar.header("📤 Upload Document")

uploaded_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file is not None:

    file_name = uploaded_file.name

    if st.session_state.uploaded_doc_name != file_name:

        with st.sidebar.spinner("Uploading & processing..."):

            try:
                res = requests.post(
                    f"{BASE_URL}/upload/",
                    files={"file": uploaded_file}
                )

                if res.status_code == 200:
                    data = res.json()

                    st.session_state.uploaded_doc_name = file_name
                    st.session_state.doc_id = data.get("doc_id")

                    st.session_state.refresh_docs = True  # 🔥 refresh registry

                    st.sidebar.success("Upload successful 🎉")
                    st.sidebar.write("Doc ID:", st.session_state.doc_id)

                    st.rerun()  # 🔥 immediate UI refresh

                else:
                    st.sidebar.error(res.text)

            except Exception as e:
                st.sidebar.error(str(e))


# =====================================================
# MAIN: DOCUMENT SELECTOR (CHAT FLOW)
# =====================================================
st.markdown("### 📄 Select Document Context")

if doc_map:

    # selected_doc_name = st.selectbox(
    #     "Choose document (or all documents)",
    #     ["All Documents"] + list(doc_map.keys())
    # )
    #
    # selected_doc_id = None if selected_doc_name == "All Documents" else doc_map[selected_doc_name]
    selected_doc_names = st.multiselect(
        "Select documents (choose 2+ for comparison)",
        list(doc_map.keys())
    )
    selected_doc_ids = [doc_map[name] for name in selected_doc_names]

    if len(selected_doc_ids) > 1:
        st.info("🔍 Comparison mode enabled")
else:
    st.info("No documents uploaded yet")
    selected_doc_id = None


# =====================================================
# QUESTION INPUT
# =====================================================
question = st.text_input("Ask a question about your policy")


# =====================================================
# ASK BUTTON
# =====================================================
if st.button("Ask"):

    if not question.strip():
        st.warning("Please enter a question")
        st.stop()


    doc_id = selected_doc_ids[0] if len(selected_doc_ids) == 1 else None
    doc_ids = selected_doc_ids if len(selected_doc_ids) > 1 else None
    print(selected_doc_ids)
    payload = {
        "question": question,
        "doc_id": doc_id,
        "doc_ids": doc_ids
    }

    try:
        res = requests.post(
            f"{BASE_URL}/ask/",
            json=payload
        )

        if res.status_code != 200:
            st.error(res.text)
            st.stop()

        data = res.json()

    except Exception as e:
        st.error(str(e))
        st.stop()


    # =================================================
    # ANSWER
    # =================================================
    st.markdown("## 💬 Answer")
    st.success(data["answer"])


    # =================================================
    # SOURCES
    # =================================================
    st.markdown("## 📚 Sources")

    for i, s in enumerate(data.get("sources", []), 1):
        st.markdown(f"""
**[{i}] Page {s.get('page')} — {s.get('file')}**
""")

        with st.expander("View evidence"):
            st.write(s.get("text"))