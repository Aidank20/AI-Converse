from groq import generate_response
import re
import streamlit as st

def looks_incomplete(text: str) -> bool:
    if not text or len(text.strip()) < 10:
        return True
    t = text.strip()
    if t.endswith(("**", "*", "-", "—", ":", ",", "(", "[", "{")):
        return True
    if re.search(r"\d+\.\s*\*\*$", t):  # like "3. **"
        return True
    if not re.search(r"[.!?]\s*$", t):  # no sentence-ending punctuation
        return True
    return False

def complete_answer(question: str, max_rounds: int = 2) -> str:
    base_prompt = (
        "Answer clearly in numbered points. "
        "Do not cut sentences. Finish each point fully.\n\n"
        f"Question: {question}"
    )
    ans = generate_response(base_prompt, temperature=0.3, max_tokens=1024)

    rounds = 0
    while rounds < max_rounds and looks_incomplete(ans):
        cont_prompt = (
            "Continue EXACTLY from where you stopped. "
            "Do NOT repeat earlier text. "
            "Finish the incomplete point and complete the answer.\n\n"
            f"Question: {question}\n\n"
            f"Answer so far:\n{ans}\n\nContinue:"
        )
        more = generate_response(cont_prompt, temperature=0.3, max_tokens=1024)
        if not more or more.strip() in ans:
            break
        ans = (ans.rstrip() + "\n" + more.lstrip()).strip()
        rounds += 1

    return ans

def main():
    st.set_page_config(page_title="AI Teaching Assistant", page_icon="🤖", layout="centered")

    # Custom CSS to align user messages to the right and center empty landing page
    st.markdown(
        """
        <style>
        /* Move user chat message bubbles to the right side */
        [data-testid="stChatMessage"]:nth-child(even) {
            flex-direction: row-reverse !important;
            text-align: right;
        }
        
        /* Adjust spacing and padding for a sleek AI interface look */
        .stChatMessage {
            border-radius: 12px;
            margin-bottom: 1rem;
        }
        
        /* Landing layout when chat history is empty */
        .hero-container {
            text-align: center;
            padding-top: 15vh;
            padding-bottom: 2vh;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Hero / Centered Header if no history exists (ChatGPT/Gemini style)
    if not st.session_state.messages:
        st.markdown(
            """
            <div class="hero-container">
                <h1>AI Teaching Assistant</h1>
                <p style="color: #666; font-size: 1.1rem;">What would you like to learn or ask about today?</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.title("AI Teaching Assistant")

    # Display existing chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Fixed Chat input at the bottom
    if user_input := st.chat_input("Ask a question..."):
        # Add user message to state and UI
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Immediate UI refresh so user message displays immediately
        st.rerun()

    # Handle completion if the last message came from the user
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        user_prompt = st.session_state.messages[-1]["content"]
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = complete_answer(user_prompt)
                st.markdown(response)
        
        # Save assistant response to state
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

if __name__ == "__main__":
    main()