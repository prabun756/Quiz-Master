# 🎓 GenAI Quiz Master

GenAI Quiz Master is an interactive Streamlit web app that generates and manages AI-powered multiple-choice quizzes on any topic using Azure OpenAI. Challenge yourself, get instant feedback, and review detailed explanations for every answer!

## Features
- AI-generated multiple choice questions on any topic
- Interactive quiz interface with immediate feedback
- Score tracking and reward system
- Detailed answer review with explanations
- Customizable number of questions
- **Displays time taken to complete the quiz in the results**

## Demo
![GenAI Quiz Master Screenshot](screenshot.png)

## Getting Started

### Prerequisites
- Python 3.8+
- [Streamlit](https://streamlit.io/)
- [openai](https://pypi.org/project/openai/)
- Azure OpenAI resource and API key

### Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/genai-quiz-master.git
   cd genai-quiz-master
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your Azure OpenAI credentials as environment variables:
   ```bash
   set AZURE_OPENAI_KEY=your_openai_key
   set AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   ```
   *(On Linux/Mac, use `export` instead of `set`)*

### Running the App
```bash
streamlit run app.py
```

## Usage
1. Enter a topic (e.g., "Python programming", "World History").
2. Click **Start Quiz** to generate questions.
3. Select your answer for each question and submit.
4. View your score, time taken, reward, and review explanations at the end.
5. Click **Restart Quiz** to try again or with a new topic.

## Output Example
- Your score and the **time taken** to complete the quiz are shown on the results page.
- You will also see a detailed review of your answers and explanations for each question.

## Screenshots
*Screenshots will be added here soon.*

## Customization
- Change the number of questions by editing the `NUM_QUESTIONS` variable in `app.py`.
- You can further style or extend the app as needed.

## License
MIT License

## Acknowledgments
- [Streamlit](https://streamlit.io/)
- [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service)

---
*Made with ❤️ using GenAI and Streamlit.*
