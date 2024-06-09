import streamlit as st
import os
import google.generativeai as genai
import os
# Initialize Gemini-Pro 
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')
fileObj = None

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini.

    See https://ai.google.dev/gemini-api/docs/prompting_with_media
    """
    try:
      file = genai.upload_file(path, mime_type=mime_type)
      st.info(f"Uploaded file '{file.display_name}' as: {file.uri}")
    except Exception as e:
      st.error(f"Error uploading file: {e}")
    return file

# Gemini uses 'model' for assistant; Streamlit uses 'assistant'
def role_to_streamlit(role):
  if role == "model":
    return "assistant"
  else:
    return role
  
def clear_chat_history():
  st.session_state.chat = model.start_chat(history=[])
  st.success("Chat history cleared!")

# Add a Gemini Chat history object to Streamlit session state
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history = [])

# Display Form Title
st.title("Chat with Google Gemini-Pro!")

# Add button to clear chat history
st.button("Clear Chat History", on_click=clear_chat_history)

# Display chat messages from history above current input box
for message in st.session_state.chat.history:
    with st.chat_message(role_to_streamlit(message.role)):
        st.markdown(message.parts[0].text)

# Accept user's next message, add to context, resubmit context to Gemini
with st.form(key="user_input", clear_on_submit=True): 
  prompt = st.text_input("I possess a well of knowledge. What would you like to know?")
  file = st.file_uploader("uploada a file")
  submit = st.form_submit_button("Send")
if submit:
  if file: 
      with st.spinner("Uploading file..."):
        os.makedirs("uploads", exist_ok=True)
        with open(os.path.join("uploads", file.name), "wb") as f:
          f.write(file.getbuffer())
      fileObj = upload_to_gemini(os.path.join("uploads", file.name), mime_type=file.type)
      st.session_state.chat.send_message(fileObj)
      # Display last
      with st.chat_message("user"):
          st.markdown(fileObj.display_name)
  if prompt:
      # Display user's last message
      st.chat_message("user").markdown(prompt)
    
     # Send user entry to Gemini and read the response
      response = st.session_state.chat.send_message(prompt) 

      # Display last 
      with st.chat_message("assistant"):
          st.markdown(response.text)