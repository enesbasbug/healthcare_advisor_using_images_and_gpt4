import streamlit as st
import base64
import os
from dotenv import load_dotenv
from openai import OpenAI
import tempfile

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

client = OpenAI()

# Initialize session state variables
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "result" not in st.session_state:
    st.session_state.result = None


st.title("Medical Help using Multimodal LLM")
st.write("Upload an image to get an analysis from GPT-4.")

# Display language selection dropdown
selected_language = st.selectbox(
    "Select the language of output:", ["English", "Turkish", "Italian"]
)

# Display the selected language
st.write(f"Selected Language for the output: {selected_language}")


uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])

# Temporary file handling
if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=os.path.splitext(uploaded_file.name)[1]
    ) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        st.session_state["filename"] = tmp_file.name

    st.image(uploaded_file, caption="Uploaded Image")


sample_prompt = f"""You are a medical practitioner and an expert in analyzing medical related images working for a very reputed hospital. You will be provided with images and you need to identify the anomalies, any disease or health issues. You need to generate the result in a detailed manner. Write all the findings, next steps, recommendations, etc. You only need to respond if the image is related to a human body and health issues. You must have to answer but also write a disclaimer saying "Consult with a Doctor before making any decisions."

Remember, if certain aspects are not clear from the image, it's okay to state 'Unable to determine based on the provided image.'

Now analyze the image and answer the above questions in the same structured manner defined above in {selected_language} Language."""


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def call_gpt4_model_for_analysis(
    filename: str, sample_prompt=sample_prompt, selected_language=selected_language
):
    selected_language = selected_language.upper()
    base64_image = encode_image(filename)

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": sample_prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                        "detail": "high",
                    },
                },
            ],
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4-vision-preview", messages=messages, max_tokens=1500
    )

    print(response.choices[0].message.content)
    return response.choices[0].message.content


# Process button
if st.button("Analyze Image"):
    if "filename" in st.session_state and os.path.exists(st.session_state["filename"]):
        st.session_state["result"] = call_gpt4_model_for_analysis(
            st.session_state["filename"]
        )
        st.markdown(st.session_state["result"], unsafe_allow_html=True)
        os.unlink(st.session_state["filename"])  # Delete the temp file after processing
