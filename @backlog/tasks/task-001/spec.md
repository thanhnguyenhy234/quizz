# Task Spec

**Task ID:** task-001
**PRD:** [prd.md](./prd.md)

## Architecture

The application will follow a simple script-based structure typical for Streamlit, with data logic separated into a utility module.

### Directory Structure
```
streamlit-quiz/
├── app.py                 # Main application entry point
├── requirements.txt       # Dependencies
├── data/
│   ├── questions.csv      # Input data
│   └── results.csv        # Output data
└── src/
    └── quiz_manager.py    # Logic for loading data and calculating scores
```

### Components

1.  **`src/quiz_manager.py`**:
    -   `load_questions(file_path: str) -> List[Dict]`: Reads CSV and returns list of question objects.
    -   `save_result(file_path: str, user_info: Dict, score: int, total: int)`: Appends result to CSV.
    -   `calculate_score(answers: Dict, questions: List[Dict]) -> int`: Compares user answers with correct ones.

2.  **`app.py`**:
    -   **Session State**: Use `st.session_state` to track if the quiz is submitted.
    -   **UI Layout**:
        -   Header/Title.
        -   Input: Full Name.
        -   Input: Permanent Address.
        -   Input: Facility Address.
        -   Form: Loop through questions to display `st.radio`.
        -   Submit Button: Triggers scoring and saving.
        -   Result Display: Shows score after submission.

## Constraints & Standards

-   **CSV Parsing**: Use Python's built-in `csv` module or `pandas` (Pandas preferred for Streamlit compatibility).
-   **Error Handling**: Gracefully handle file not found errors for `questions.csv`.
-   **State Management**: Ensure the app doesn't reset the form unexpectedly on interaction (use `st.form` for the quiz area).

## Edge Cases

1.  **Missing Data File**: Display a friendly error message if `questions.csv` is missing.
2.  **Missing User Info**: Prevent submission if any of the required fields (Name, Addresses) are empty.
3.  **Incomplete Answers**: Handle cases where user skips a question (default to wrong or force selection).
4.  **Concurrent Writes**: Since we use a local CSV, explicit file locking is out of scope, but we should append in a way that minimizes overwrite risk (standard append mode `a`).

## Data Models

**Question CSV Schema:**
-   `id`: Unique ID
-   `question`: Text of the question
-   `option_A`: Text for option A
-   `option_B`: Text for option B
-   `option_C`: Text for option C
-   `option_D`: Text for option D
-   `answer`: The correct option key (e.g., 'A', 'B', 'C', 'D')

**Result CSV Schema:**
-   `timestamp`: ISO 8601 datetime
-   `full_name`: String
-   `permanent_address`: String
-   `facility_address`: String
-   `score`: Integer
-   `total`: Integer
