# main.py (Streamlit)
# Switch provider by changing the import line:
#from groq import generate_response
from hf import generate_response

import re
import streamlit as st

def looks_incomplete(text: str) -> bool:
    if not text or len(text.strip()) < 10:
        return True
    t = text.strip()
    # common "cut" signs: ends mid-word, mid-markdown, or no closing punctuation
    if t.endswith(("**", "*", "-", "—", ":", ",", "(", "[", "{")):
        return True
    if re.search(r"\d+\.\s*\*\*$", t):  # like "3. **"
        return True
    if not re.search(r"[.!?]\s*$", t):  # no sentence-ending punctuation
        return True
    return False

def complete_answer(question: str, max_rounds: int = 2) -> str:
    # 1) Ask for a clean structured answer (helps avoid unfinished bullets)
    base_prompt = (
        "Answer clearly in numbered points. "
        "Do not cut sentences. Finish each point fully.\n\n"
        f"Question: {question}"
    )

    ans = generate_response(base_prompt, temperature=0.3, max_tokens=1024)

    # 2) If it looks cut, continue from last line without repeating
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
    st.title("AI Teaching Assistant")
    st.write("Welcome! You can ask me anything about various subjects, and I'll provide an answer.")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Enter your question here:")

    if user_input:
        resposnse = complete_answer(user_input)
        st.session_state.chat_history.append((user_input, resposnse))
    if st.session_state.chat_history:
        st.subheader("Chat History")
        for i, chat in enumerate(st.session_state.chat_history, 1):
            st.markdown(f"**Q{i}:** {chat['question']}**")
            st.markdown(f"{chat['answer']}")
if __name__ == "__main__":
    main()
