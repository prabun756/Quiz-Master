"""
GenAI Quiz Master - A Streamlit application that generates and manages interactive quizzes.
Features:
- AI-generated multiple choice questions on any topic
- Interactive quiz interface with immediate feedback
- Score tracking and rewards system
- Detailed answer review with explanations
"""

import streamlit as st
from openai import AzureOpenAI
import os
import time

# Azure OpenAI Configuration
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-12-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Application Configuration
st.set_page_config(page_title="🎓 GenAI Quiz Master", layout="centered")
st.title("🎓 GenAI Quiz Master")
NUM_QUESTIONS = 6
st.markdown(f"Test your knowledge with {NUM_QUESTIONS} AI-generated MCQs on your favorite topic!")

# Initialize session state variables for quiz management
if "questions" not in st.session_state:
    for key in ["questions", "current_q", "score", "quiz_started", "quiz_complete", "user_answers"]:
        st.session_state[key] = [] if key == "questions" else 0 if key in ["current_q", "score"] else False if key in ["quiz_started", "quiz_complete"] else {}

def generate_mcqs(topic):
    """
    Generate multiple choice questions using Azure OpenAI.
    Args:
        topic (str): The topic to generate questions about
    Returns:
        str: Raw response containing formatted questions
    """
    prompt = f"""
Generate exactly {NUM_QUESTIONS} multiple-choice questions on the topic "{topic}".
Follow this exact format for EACH question, with exactly one empty line between questions:

Q: <question>
A. <option A>
B. <option B>
C. <option C>
D. <option D>
Answer: <letter>
Explanation: <explanation>

Repeat this exact format {NUM_QUESTIONS} times. Make sure to include one empty line between each question.
Do not include any additional text or formatting, except for question to start with "Q1:, Q2:, ...".
"""
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

def parse_questions(text):
    """
    Parse the raw question text into structured format.
    Args:
        text (str): Raw question text from OpenAI
    Returns:
        list: List of dictionaries containing parsed questions
    Raises:
        st.error: If unable to parse the expected number of questions
    """
    try:
        # Clean up text first - handle extra spaces and normalize line endings
        text = text.replace('\r\n', '\n')  # Normalize line endings
        text = '\n'.join(line.strip() for line in text.split('\n'))  # Remove extra spaces
        text = text.replace('\n\n\n', '\n\n')  # Remove extra blank lines
        
        print("\nOriginal text after cleanup:")
        print(text)  # Print cleaned text for debugging
        print(f"\n{'='*50}")
        print(f"Starting to parse questions...")
        print(f"Expected number of questions: {NUM_QUESTIONS}")
        print(f"Raw text length: {len(text)} characters")
        
        questions = []
        # Split by Q but handle numbered questions (Q1:, Q2:, etc.)
        blocks = text.strip().split("\n\n")
        print(f"Found {len(blocks)} blocks after splitting")
        
        for idx, block in enumerate(blocks, 1):
            if not block.strip().startswith("Q"):
                continue
                
            try:
                lines = block.split('\n')
                question = lines[0].split(":", 1)[1].strip() if ":" in lines[0] else lines[0].strip()
                
                # Get option lines (should be next 4 lines)
                option_lines = [line for line in lines if any(line.strip().startswith(f"{opt}.") for opt in ["A", "B", "C", "D"])]
                if len(option_lines) != 4:
                    print(f"Skipping Q{idx}: Wrong number of options")
                    continue
                
                options = {}
                for line in option_lines:
                    opt_letter = line[0]
                    options[opt_letter] = line[2:].strip()
                
                # Find answer and explanation lines
                answer_line = next((line for line in lines if line.strip().startswith("Answer:")), "")
                explanation_line = next((line for line in lines if line.strip().startswith("Explanation:")), "")
                
                if not answer_line or not explanation_line:
                    print(f"Skipping Q{idx}: Missing answer or explanation")
                    continue
                
                answer = answer_line.replace("Answer:", "").strip()
                explanation = explanation_line.replace("Explanation:", "").strip()
                
                if answer not in ["A", "B", "C", "D"]:
                    print(f"Skipping Q{idx}: Invalid answer format '{answer}'")
                    continue
                
                print(f"Successfully parsed Q{idx}")
                questions.append({
                    "question": question,
                    "options": options,
                    "answer": answer,
                    "explanation": explanation
                })
            except Exception as e:
                print(f"Error parsing Q{idx}: {str(e)}")
                continue
        
        print(f"\nParsing complete. Found {len(questions)} valid questions")
        if len(questions) < NUM_QUESTIONS:
            st.error(f"Could not generate {NUM_QUESTIONS} valid questions. Please try again.")
            return []
        
        return questions[:NUM_QUESTIONS]
    except Exception as e:
        st.error(f"Error parsing questions: {str(e)}. Please try again.")
        return []

# Quiz Initialization Interface
if not st.session_state.quiz_started:
    topic = st.text_input("Enter a topic to begin:", "")
    if st.button("Start Quiz") and topic:        
        try:
            with st.spinner("Generating questions..."):
                raw = generate_mcqs(topic)
                print(f"Generated raw text length: {len(raw)}")
                questions = parse_questions(raw)
                print(f"Parsed {len(questions)} valid questions")
                if not questions:  # If we couldn't generate enough valid questions
                    st.error("Failed to generate questions. Please try again with a different topic.")
                else:
                    st.session_state.questions = questions
                    st.session_state.quiz_started = True
                    st.session_state.current_q = 0
                    st.session_state.score = 0
                    st.session_state.user_answers = {}
                    st.session_state.quiz_complete = False
                    time.sleep(0.1)
                    st.rerun()
        except Exception as e:
            st.error(f"An error occurred: {str(e)}. Please try again.")

# Main Quiz Interface - Display questions and handle answers
if st.session_state.quiz_started and not st.session_state.quiz_complete:
    q = st.session_state.questions[st.session_state.current_q]
    st.markdown(f"### Question {st.session_state.current_q + 1} of {NUM_QUESTIONS}")
    st.markdown(f"**{q['question']}**")

    # Display radio buttons for answer options
    selected = st.radio("Choose your answer:", list(q["options"].keys()),
                        format_func=lambda x: f"{x}. {q['options'][x]}", key=f"q_{st.session_state.current_q}")

    # Handle answer submission
    if st.button("Submit Answer"):
        st.session_state.user_answers[st.session_state.current_q] = selected
        if selected == q["answer"]:
            st.session_state.score += 1
        if st.session_state.current_q < NUM_QUESTIONS - 1:
            st.session_state.current_q += 1
            # Reset radio selection for next question
            for key in list(st.session_state.keys()):
                if key.startswith('q_'):
                    del st.session_state[key]
            time.sleep(0.1)
            st.rerun()
        else:
            st.session_state.quiz_complete = True

# Results and Review Interface
if st.session_state.quiz_complete:
    st.success("🎉 Quiz Complete!")
    st.markdown(f"### Your Score: {st.session_state.score} / {NUM_QUESTIONS}")

    # Calculate and display score with appropriate feedback
    score_percentage = (st.session_state.score / NUM_QUESTIONS) * 100
    
    if score_percentage > 50:
        st.balloons()
        st.success("🏆 Excellent! You earned a reward badge!")
        st.markdown("""
        <div style='padding: 20px; background-color: #f0f8ff; border-radius: 10px; text-align: center'>
            <h3>🌟 Achievement Unlocked! 🌟</h3>
            <p style='font-size: 18px'>You've mastered this topic!</p>
            <div style='font-size: 40px'>🏆</div>
        </div>
        """, unsafe_allow_html=True)
    elif score_percentage == 50:
        st.info("👍 Good job! Try again for a reward!")
    else:
        st.warning("📘 Keep learning! You can do better next time.")

    # Display detailed answer review
    st.markdown("---")
    st.markdown("### Review Your Answers:")
    for i, q in enumerate(st.session_state.questions):
        st.markdown(f"**Q{i+1}: {q['question']}**")
        for opt_key, opt_val in q["options"].items():
            style = ""
            if opt_key == q["answer"]:
                style = "color: green; font-weight: bold;"
            elif opt_key == st.session_state.user_answers.get(i):
                style = "color: red;"
            st.markdown(f"<span style='{style}'>{opt_key}. {opt_val}</span>", unsafe_allow_html=True)
        if st.session_state.user_answers.get(i) == q["answer"]:
            st.success(f"✅ Your answer: {q['answer']}")
        else:
            st.error(f"❌ Your answer: {st.session_state.user_answers.get(i)} | Correct: {q['answer']}")
        st.info(f"**Explanation:** {q['explanation']}")
        st.markdown("---")

    # Reset quiz state for new attempt
    if st.button("Restart Quiz"):
        for key in ["questions", "current_q", "score", "quiz_started", "quiz_complete", "user_answers"]:
            st.session_state[key] = [] if key == "questions" else 0 if key in ["current_q", "score"] else False if key in ["quiz_started", "quiz_complete"] else {}
        for key in list(st.session_state.keys()):
            if key.startswith('q_'):
                del st.session_state[key]
        time.sleep(0.1)
        st.rerun()
