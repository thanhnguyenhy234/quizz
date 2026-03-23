# Multiple Choice Question Generator

## Purpose

Generate multiple-choice questions with 4 options from question-answer pairs. Uses AI (Claude) to create plausible distractors.

## Requirements

```bash
pip install anthropic
```

Or use the provided requirements.txt:

```bash
pip install -r .opencode/skills/question-generator/requirements.txt
```

## Setup

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Usage

### Command Line

```bash
python .opencode/skills/question-generator/generate_mcq.py \
  --input input_qa.csv \
  --output questions.csv
```

### Input Format

CSV file with columns: `question,answer`

Example:

```csv
question,answer
"What is the capital of France?","Paris"
"What is 2 + 2?","4"
```

### Output Format

CSV file with columns: `question,option_a,option_b,option_c,option_d,correct_option`

The correct answer is randomly placed among options A-D.

### Python API

```python
from generate_mcq import MCQGenerator

# Initialize
generator = MCQGenerator()  # Uses ANTHROPIC_API_KEY env var

# Generate single question
mcq = generator.generate_question(
    question="What is the capital of France?",
    correct_answer="Paris"
)

# Generate from pairs
qa_pairs = [
    ("What is 2 + 2?", "4"),
    ("Who wrote Hamlet?", "William Shakespeare")
]
questions = generator.generate_from_pairs(qa_pairs)

# Save to CSV
generator.save_to_csv(questions, "output.csv")
```

## Features

- **AI-powered distractors**: Uses Claude to generate plausible wrong answers
- **Random positioning**: Correct answer randomly placed in A-D positions
- **CSV I/O**: Simple CSV input/output format compatible with quiz apps
- **Batch processing**: Process multiple questions efficiently

## Integration with streamlit-quizz

Compatible with existing `data/questions.csv` format (task-001). Generate questions separately, then use in quiz app.

## Constraints

- Requires Anthropic API key (paid API)
- Generates 3 distractors per question
- Output format matches task-001 spec: `question,option_a,option_b,option_c,option_d,correct_option`

## Sample Test

```bash
cd .opencode/skills/question-generator
python generate_mcq.py -i sample_input.csv -o sample_output.csv
```

## Error Handling

- Validates API key presence
- Ensures exactly 4 options per question
- Handles missing anthropic package gracefully
