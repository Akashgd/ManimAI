import streamlit as st
import google.generativeai as genai
import subprocess
import os

# Configure the Google AI API
genai.configure(api_key="AIzaSyClZYPLjZjIp9A_8B8TvkLkaBy23Rr0dP0")

st.set_page_config(layout="wide")  # Set the layout to wide mode

st.title("Create Animations")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Create two columns with adjusted widths
col1, col2 = st.columns([1, 1])  # Adjust the proportions as needed

# Left column for chat
with col1:
    st.subheader("Enter prompt to create mathematical animations")

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Enter a prompt here"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Generate response from Google AI API
        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                ],
                generation_config={
                    "temperature": 1,
                    "top_p": 0.95,
                    "top_k": 64,
                    "max_output_tokens": 8192,
                    "response_mime_type": "text/plain",
                },
            )

            chat_session = model.start_chat(history=[])
            ai_prompt = f"Generate only the Manim script code for the following prompt: {prompt}. Do not include any explanations or comments, only the Python code."
            response = chat_session.send_message(ai_prompt)
            manim_script = response.text.strip()  # Ensure no extra text
            print(manim_script)
            # Remove first and last lines if they contain triple backticks
            manim_script_lines = manim_script.splitlines()
            if manim_script_lines[0].startswith("```"):
                manim_script_lines = manim_script_lines[1:]
            if manim_script_lines[-1].startswith("```"):
                manim_script_lines = manim_script_lines[:-1]
            manim_script = "\n".join(manim_script_lines)

            # Save the generated Manim script to a file
            script_filename = "generated_manim_script.py"
            with open(script_filename, "w") as file:
                file.write(manim_script)

            # Display AI response in chat
            with st.chat_message("bot"):
                st.markdown(f"Manim script generated and saved to `{script_filename}`")

            # Add AI response to chat history
            st.session_state.messages.append({"role": "bot", "content": f"Manim script generated and saved to `{script_filename}`"})

            # Run the Manim script and generate the animation video
            video_output_dir = "media/videos/generated_manim_script/480p15"
            video_filename = os.path.join(video_output_dir, "GeneratedScene.mp4")

            # Create the output directory if it doesn't exist
            os.makedirs(video_output_dir, exist_ok=True)

            result = subprocess.run(["manim", "-ql", script_filename, "-o", "GeneratedScene"], capture_output=True, text=True)
            
            if result.returncode != 0:
                st.error(f"Error generating video: {result.stderr}")
            else:
                st.success(f"Animation video generated successfully: {video_filename}")

        except Exception as e:
            st.error(f"Error generating response: {e}")

# Right column for bordered area
with col2:
    st.subheader("Result")
    if st.session_state.messages:
        # Extract the latest response from the bot to display in the bordered area
        latest_response = next((msg for msg in reversed(st.session_state.messages) if msg["role"] == "bot"), None)
        if latest_response:
            st.markdown(
                f"""
                <div style="border: 1px solid black; padding: 10px;">
                    <pre>{latest_response["content"]}</pre>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Check if the video file exists and display it
            if os.path.exists(video_filename):
                video_file = open(video_filename, "rb")
                video_bytes = video_file.read()
                st.video(video_bytes)
    else:
        st.markdown(
            """
            <div style="border: 1px solid black; padding: 10px;">
                <p>This is a simple bordered area where the generated Manim script will be displayed.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
