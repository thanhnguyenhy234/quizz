# Task PRD

**Task ID:** task-001
**Created:** 2025-11-22

## Goal

Create a Streamlit web application that collects and stores multiple-choice test results from users, using a CSV file as the question source.

## Scope

**In-Scope:**

- **Repository Setup**: Initialize Git repository with proper structure (`src/`, `data/`, `tests/`).
- **Quiz Interface**: Streamlit app to display questions one by one or all at once (single page).
- **Data Loading**: Functionality to read questions from `data/questions.csv`.
- **User Input**: Form for user details (Full Name, Permanent Address, Facility Address) and radio buttons for selecting answers.
- **Scoring**: Logic to calculate the score upon submission.
- **Result Storage**: Append user results (Name, Score, Timestamp) to `data/results.csv`.

**Out-of-Scope:**

- User Authentication (Login/Signup).
- Database integration (SQLite/PostgreSQL) - usage of CSV is sufficient for MVP.
- Admin dashboard for analytics.
- Real-time leaderboard.

## Success Criteria

- [x] Repository created with `app.py`, `requirements.txt`, and `README.md`.
- [x] Application reads questions dynamically from `data/questions.csv`.
- [x] User can select answers for all questions and submit.
- [x] App displays the final score to the user after submission.
- [x] Submission appends a new row to `data/results.csv` with Timestamp, User, and Score.
- [x] Basic error handling exists (e.g., missing CSV file).

## Constraints

- **Tech Stack**: Python 3.10+, Streamlit.
- **Data Format**:
  - `questions.csv`: `id,question,option_a,option_b,option_c,option_d,correct_option`
  - `results.csv`: `timestamp,full_name,permanent_address,facility_address,score,total_questions`
- **Deployment**: Must be runnable locally via `streamlit run app.py`.
