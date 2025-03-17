import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain.vectorstores import FAISS
from langchain import PromptTemplate
from langchain_community.embeddings import HuggingFaceInstructEmbeddings

# Set API Key for Groq
os.environ["GROQ_API_KEY"] = "***************"

# Initialize Language Model
def load_groq_model():
    return ChatGroq(model_name="llama-3.3-70b-specdec", temperature=0.7)

# Load Embedding Model
def load_embedding_model():
    return HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-base")

# Load FAISS Vector Store
def load_vector_store(vector_path, db_file_name, embedding_model):
    return FAISS.load_local(
        folder_path=os.path.join(vector_path, db_file_name),
        embeddings=embedding_model,
        index_name="minmarn",
        allow_dangerous_deserialization=True
    ).as_retriever()

# Define Chatbot Prompt Template
def get_prompt_template():
    template = """
    Please answer the following question accurately based on the provided context of a person named Min Marn Ko.
    
    Context:
    {context}
    
    Question: {question}
    
    Gentle & Informative Answer:
    """.strip()
    return PromptTemplate.from_template(template)

# Streamlit UI Setup
def setup_ui():
    st.set_page_config(page_title="Min Marn Ko Chatbot", layout="wide")
    st.title("🤖 Min Marn Ko Chatbot")

# Chatbot Function
def chatbot():
    setup_ui()
    
    # Load models
    groq_model = load_groq_model()
    embedding_model = load_embedding_model()
    retriever = load_vector_store("vector-store", "Marn", embedding_model)
    prompt_template = get_prompt_template()

    # Initialize Chat History
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # User Input
    user_input = st.text_input("Type your message here:", key="input")

    if st.button("Send") and user_input:
        # Retrieve relevant documents
        retrieved_docs = retriever.get_relevant_documents(user_input)
        context = "\n".join([doc.page_content[:500] for doc in retrieved_docs])
        
        # Format prompt
        formatted_prompt = prompt_template.format(context=context, question=user_input)
        
        # Generate response
        response = groq_model.invoke(formatted_prompt)
        
        # Store and display chat history
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("Chatbot", response))
        
        for speaker, text in st.session_state.chat_history:
            st.write(f"**{speaker}:** {text}")
        
        # Display supporting documents
        st.subheader("📄 Supporting Documents:")
        for i, doc in enumerate(retrieved_docs):
            st.write(f"🔹 **Document {i+1}:** {doc.page_content[:300]}...")

# Run the chatbot
if __name__ == "__main__":
    chatbot()