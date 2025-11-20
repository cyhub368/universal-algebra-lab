import streamlit as st
import google.generativeai as genai
import matplotlib.pyplot as plt
import numpy as np
import re

# --- CONFIGURATION ---
st.set_page_config(page_title="Universal Math Lab", page_icon="🧠")

# 1. Get API Key (Securely)
# You will enter this in Streamlit Secrets later.
# If running locally, you can replace st.secrets["GEMINI_API_KEY"] with "YOUR_KEY_HERE"
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.warning("⚠️ API Key missing. Please add GEMINI_API_KEY to your Streamlit Secrets.")

# --- THE AI BRAIN (SYSTEM PROMPT) ---
def get_visualization_code(user_query):
    """
    Asks the AI to write Python code to visualize the student's math question.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    You are a Visual Math Tutor for High School Algebra.
    The student asked: "{user_query}"

    Goal: Write a PYTHON script using 'matplotlib.pyplot' (as plt) and 'numpy' (as np) to visualize this concept.
    
    Rules:
    1. The code must create a figure: fig, ax = plt.subplots()
    2. It must plot the relevant graph, shape, or animation frame.
    3. It must NOT show the plot (plt.show()). It must just create the 'fig' object.
    4. Add clear labels, grid lines, and a title.
    5. Do NOT use input() or interactive sliders inside the code (static visual only for now).
    6. Output ONLY the raw Python code. No markdown ``` ticks. No explanations.
    
    Example output format:
    import numpy as np
    import matplotlib.pyplot as plt
    x = np.linspace(-10, 10, 100)
    fig, ax = plt.subplots()
    ax.plot(x, x**2)
    """
    
    response = model.generate_content(prompt)
    # Clean up code (remove markdown tags if the AI adds them)
    clean_code = re.sub(r"```python|```", "", response.text).strip()
    return clean_code

def get_explanation(user_query):
    """
    Asks the AI for a simple text explanation (Gate 1/2/3 Style).
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"Explain this algebra concept to a high schooler simply (3 sentences max): {user_query}"
    return model.generate_content(prompt).text

# --- THE UI ---
st.title("🧪 The Universal Algebra Lab")
st.markdown("Ask *any* question. The AI will build a custom graph for you.")

# Input
query = st.text_input("What do you want to visualize?", placeholder="e.g., Graph y = 3x - 2, or Show me a circle with radius 5")

if st.button("Build Visualization"):
    if not query:
        st.error("Please type a question first!")
    else:
        with st.spinner("🤖 The AI is writing code for you..."):
            try:
                # 1. Get the Explanation
                explanation = get_explanation(query)
                st.success(explanation)
                
                # 2. Get the Code
                code = get_visualization_code(query)
                
                # 3. Execute the Code (The Magic Trick)
                # We create a local dictionary to capture the 'fig' variable from the AI's code
                local_vars = {}
                exec(code, globals(), local_vars)
                
                # 4. Display
                if 'fig' in local_vars:
                    st.pyplot(local_vars['fig'])
                else:
                    st.error("The AI wrote code, but didn't create a 'fig' variable. Try rephrasing.")
                    
                # Optional: Show the code to the students so they can learn Python too!
                with st.expander("See the Python Code behind this"):
                    st.code(code, language='python')
                    
            except Exception as e:
                st.error(f"Oops! The AI wrote bad code. Try again. Error: {e}")
