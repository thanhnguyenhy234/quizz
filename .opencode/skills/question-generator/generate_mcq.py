"""
Multiple Choice Question Generator

Generates 4-option multiple choice questions from a question and correct answer.
Uses AI to create plausible distractors.
"""

import csv
import sys
from typing import List, Dict, Optional
import os

try:
    import anthropic
except ImportError:
    print("Error: anthropic package not installed. Install with: pip install anthropic", file=sys.stderr)
    sys.exit(1)


class MCQGenerator:
    """Generate multiple choice questions with 4 options."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the MCQ generator.
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def generate_question(self, question: str, correct_answer: str) -> Dict[str, str]:
        """
        Generate a multiple choice question with 4 options.
        
        Args:
            question: The question text
            correct_answer: The correct answer
            
        Returns:
            Dictionary with keys: question, option_a, option_b, option_c, option_d, correct_option
        """
        prompt = f"""Given this question and correct answer, generate 3 plausible but incorrect distractor options.

Question: {question}
Correct Answer: {correct_answer}

Requirements:
- Generate exactly 3 incorrect options that are plausible but clearly wrong
- Make distractors similar in length and format to the correct answer
- Avoid obvious patterns (e.g., "all of the above")
- Return ONLY the 3 distractors, one per line, no numbering or labels"""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse distractors from response
        response_text = message.content[0].text.strip()
        distractors = [line.strip() for line in response_text.split('\n') if line.strip()][:3]
        
        # Ensure we have exactly 3 distractors
        while len(distractors) < 3:
            distractors.append(f"Incorrect option {len(distractors) + 1}")
        
        # Randomize position of correct answer
        import random
        options = distractors + [correct_answer]
        random.shuffle(options)
        
        correct_letter = chr(65 + options.index(correct_answer))  # A, B, C, or D
        
        return {
            'question': question,
            'option_a': options[0],
            'option_b': options[1],
            'option_c': options[2],
            'option_d': options[3],
            'correct_option': correct_letter
        }
    
    def generate_from_pairs(self, qa_pairs: List[tuple]) -> List[Dict[str, str]]:
        """
        Generate multiple MCQs from question-answer pairs.
        
        Args:
            qa_pairs: List of (question, answer) tuples
            
        Returns:
            List of question dictionaries
        """
        questions = []
        for i, (question, answer) in enumerate(qa_pairs, 1):
            print(f"Generating question {i}/{len(qa_pairs)}...", file=sys.stderr)
            mcq = self.generate_question(question, answer)
            questions.append(mcq)
        return questions
    
    def save_to_csv(self, questions: List[Dict[str, str]], output_file: str):
        """
        Save generated questions to CSV file.
        
        Args:
            questions: List of question dictionaries
            output_file: Output CSV file path
        """
        fieldnames = ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(questions)
        
        print(f"Saved {len(questions)} questions to {output_file}", file=sys.stderr)


def main():
    """CLI interface for question generation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate multiple choice questions')
    parser.add_argument('--input', '-i', required=True, help='Input CSV with columns: question,answer')
    parser.add_argument('--output', '-o', required=True, help='Output CSV file')
    parser.add_argument('--api-key', help='Anthropic API key (or use ANTHROPIC_API_KEY env var)')
    
    args = parser.parse_args()
    
    # Read input Q&A pairs
    qa_pairs = []
    with open(args.input, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'question' in row and 'answer' in row:
                qa_pairs.append((row['question'], row['answer']))
    
    print(f"Loaded {len(qa_pairs)} question-answer pairs", file=sys.stderr)
    
    # Generate MCQs
    generator = MCQGenerator(api_key=args.api_key)
    questions = generator.generate_from_pairs(qa_pairs)
    
    # Save to CSV
    generator.save_to_csv(questions, args.output)
    print("Done!", file=sys.stderr)


if __name__ == '__main__':
    main()
