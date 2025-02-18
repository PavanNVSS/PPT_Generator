# # app.py
import qdrant_client
from sentence_transformers import SentenceTransformer
import streamlit as st
from langchain_community.vectorstores import Qdrant
from model import generate_response
import ui
from powerpoint import save_presentation

# Set the page configuration
st.set_page_config(
    page_title="PPT Generator",
    page_icon="📊",
    layout="wide",  # Can be "centered" or "wide"
    initial_sidebar_state="expanded",
)


if "previous_theme" not in st.session_state:
    st.session_state["previous_theme"] = None
if "ppt_generated" not in st.session_state:
    st.session_state["ppt_generated"] = False
if "ppt_path" not in st.session_state:
    st.session_state["ppt_path"] = None


model_name = "all-MiniLM-L6-v2"
model = SentenceTransformer(model_name)


class SentenceTransformerEmbeddings:
    def __init__(self, model):
        self.model = model

    def embed_query(self, text: str) -> list[float]:
        embedding = self.model.encode([text])[0]
        return embedding.tolist()

    def embed(self, texts):
        return self.model.encode(texts)



embeddings = SentenceTransformerEmbeddings(model=model)

# Set up connection to Qdrant Cloud
client = qdrant_client.QdrantClient(
    url="https://12dca0ba-749f-4b79-b71a-8a7e36bbe007.us-west-2-0.aws.cloud.qdrant.io",
    api_key="ha6xk8yCA44Eg_2HyE9vsFjutkperpSD7MqJ25NV1jpM7RmWxdaCFg",
    timeout=300
)

db = Qdrant(client=client, embeddings=embeddings.embed, collection_name="vector_db")

ui.show_title()
user_inputs = ui.user_inputs()

ppt_name = user_inputs['ppt_name']
theme = user_inputs['theme']
slide_count = user_inputs['slide_count']
additional_info = user_inputs['additional_info']

query = ui.user_input()

ui.handle_submission(query)

# Handle query submission
if st.session_state.get('submit_clicked', False):
    if query:
        print("Query:", query)
        print("Query type:", type(query))

        valid_docs = client.search(
            collection_name="vector_db",
            query_vector=embeddings.embed_query(str(query)),
            limit=5,
            with_vectors=True
        )
        valid_docs = [
            doc for doc in valid_docs if doc.payload.get('text') and isinstance(doc.payload['text'], str)
        ]

        if valid_docs:
            # Join the text from all valid documents
            retrieved_content = "\n\n".join([doc.payload['text'] for doc in valid_docs])
            ui.display_retrieved_content(retrieved_content)

            response = generate_response(query, retrieved_content, slide_count, additional_info, use_api=True)
            ui.display_refined_response(response)

            if st.session_state["ppt_generated"] and st.session_state["previous_theme"] != theme:
                st.warning("The theme has been changed. Do you want to regenerate the PPT with the updated design?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Generate PPT with Updated Design"):
                        ppt_path = save_presentation(response, ppt_name, theme, slide_count, additional_info)
                        st.session_state["ppt_path"] = ppt_path
                        st.session_state["ppt_generated"] = True
                        st.session_state["previous_theme"] = theme
                        st.success("PPT has been regenerated with the updated design!")
                        with open(ppt_path, "rb") as ppt_file:
                            st.download_button(
                                label="Download PowerPoint",
                                data=ppt_file,
                                file_name=f"{ppt_name}.pptx",
                                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                            )
                with col2:
                    if st.button("Cancel"):
                        st.info("The design change was canceled. The existing PPT remains unchanged.")
                        if st.session_state["ppt_path"]:
                            with open(st.session_state["ppt_path"], "rb") as ppt_file:
                                st.download_button(
                                    label="Download Existing PowerPoint",
                                    data=ppt_file,
                                    file_name=f"{ppt_name}.pptx",
                                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                                )
            else:
                if st.button("Generate PowerPoint"):
                    ppt_path = save_presentation(response, ppt_name, theme, slide_count, additional_info)
                    st.session_state["ppt_path"] = ppt_path
                    st.success(f"PowerPoint saved at: {ppt_path}")
                    with open(ppt_path, "rb") as ppt_file:
                        st.download_button(
                            label="Download PowerPoint",
                            data=ppt_file,
                            file_name=f"{ppt_name}.pptx",
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                        )
                    st.session_state["ppt_generated"] = True
                    st.session_state["previous_theme"] = theme
        else:
            ui.display_warning("No valid content found in the database.")
