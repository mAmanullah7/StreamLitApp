# StreamLitApp

A Streamlit app that provides a chat-based assistant for analyzing customer feedback data.

## Run the app locally

1. Open the project folder:
   ```bash
   cd /Users/mohammadamanullah/Desktop/Study\ Material/StreamLitApp
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your OpenAI API key:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```

6. Open the local URL shown in the terminal, usually:
   ```text
   http://localhost:8501
   ```

## Notes

- The app will create a `Chats` folder automatically to store chat history.
- If you are using a different shell, activate the virtual environment with the appropriate command for that shell.