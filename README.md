# 📝 Streamlit Quiz Application

A simple multiple-choice quiz application built with Streamlit that reads questions from a CSV file, collects user responses, and stores results.

## Features

- Load questions dynamically from CSV file
- Collect user information (name and addresses)
- Multiple-choice question interface with radio buttons
- Automatic scoring and result display
- Persistent result storage in CSV format
- Error handling for missing files and incomplete submissions

## Project Structure

```
streamlit-quiz/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── data/
│   ├── questions.csv           # Quiz questions (input)
│   ├── results.csv             # Quiz results summary (output)
│   └── results_details.csv     # Detailed answers per question (output)
└── src/
    └── quiz_manager.py         # Quiz logic (load, score, save)
```

## Installation

1. Clone this repository (or download the files)

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. **Prepare Questions File**

   Ensure `data/questions.csv` exists with the following format:

   ```csv
   id,question,option_A,option_B,option_C,option_D,answer
   1,What is the capital of France?,Berlin,Madrid,Paris,Rome,C
   2,Which programming language is known for web development?,Python,Java,JavaScript,C++,C
   ```

   - `answer` should be A, B, C, or D (matching the correct option)

2. **Run the Application**

   ```bash
   streamlit run app.py
   ```

3. **Take the Quiz**
   - Fill in your personal information (all fields required)
   - Answer all questions by selecting radio buttons
   - Click "Submit Quiz" to see your score
   - Results are automatically saved to `data/results.csv` and `data/results_details.csv`

## Data Format

### Questions CSV (`data/questions.csv`)

| Column   | Description              |
| -------- | ------------------------ |
| id       | Unique question ID       |
| question | Question text            |
| option_A | First option             |
| option_B | Second option            |
| option_C | Third option             |
| option_D | Fourth option            |
| answer   | Correct answer (A/B/C/D) |

### Results CSV (`data/results.csv`)

Lưu tổng hợp điểm số cho mỗi người dùng:

| Column            | Description               |
| ----------------- | ------------------------- |
| timestamp         | ISO 8601 timestamp        |
| full_name         | User's full name          |
| permanent_address | User's permanent address  |
| facility_address  | User's facility address   |
| score             | Number of correct answers |
| total_questions   | Total number of questions |

### Results Details CSV (`data/results_details.csv`)

Lưu chi tiết từng câu trả lời của người dùng:

| Column         | Description                                          |
| -------------- | ---------------------------------------------------- |
| timestamp      | ISO 8601 timestamp (same as results.csv for linking) |
| full_name      | User's full name                                     |
| question_id    | Question ID                                          |
| question_text  | Full question text                                   |
| user_answer    | User's answer (A/B/C/D or "Not answered")            |
| correct_answer | Correct answer (A/B/C/D)                             |
| is_correct     | Whether answer is correct (Yes/No)                   |

## Error Handling

The application handles:

- Missing `questions.csv` file (displays error message)
- Malformed CSV files (validates required columns)
- Empty user information fields (prevents submission)
- Incomplete quiz answers (requires all questions answered)

## Requirements

- Python 3.10 or higher
- Streamlit 1.28.0 or higher
- Pandas 2.0.0 or higher

## License

This project is open source and available for educational purposes.
