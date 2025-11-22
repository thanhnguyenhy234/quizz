"""Quiz Manager Module

This module handles loading questions from CSV, calculating scores,
and saving results to CSV. Also integrates with Telegram for notifications.
"""

import pandas as pd
import subprocess
import socket
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict


def check_connection(host="api.telegram.org", port=443, timeout=5):
    """Check internet connection to Telegram API.
    
    Args:
        host: Host to check connection to
        port: Port number
        timeout: Timeout in seconds
        
    Returns:
        True if connection is available, False otherwise
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(f"Network error: {ex}")
        return False


def all_send_warp(chat_id, bot_token, file_path):
    """Send file via Telegram with Cloudflare Warp management.
    
    Args:
        chat_id: Telegram chat ID
        bot_token: Telegram bot token
        file_path: Path to file to send
        
    Returns:
        Response JSON from Telegram API
    """
    try:
        # Try to disconnect Warp
        try:
            subprocess.run(["warp-cli", "disconnect"], check=True)
            print("Warp disconnected.")
            time.sleep(2)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warp not available, continuing without disconnect.")
        
        # Check connection
        if not check_connection():
            print("Cannot connect to Telegram API. Checking connection...")
            return None
        
        # Send file via Telegram
        url = f"https://cool-butterfly-9ded.tungson92dkh.workers.dev//bot{bot_token}/sendDocument"
        with open(file_path, "rb") as file:
            files = {"document": file}
            data = {"chat_id": chat_id}
            response = requests.post(url, files=files, data=data, timeout=10)
            print(f"File sent successfully to Telegram: {file_path}")
            return response.json()
            
    except Exception as e:
        print(f"Error sending file: {e}")
        return None
    finally:
        # Try to reconnect Warp
        try:
            subprocess.run(["warp-cli", "connect"], check=True)
            print("Warp reconnected.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warp reconnection skipped.")


def send_file_hnd(file_path):
    """Send file to HND Telegram group.
    
    Args:
        file_path: Path to file to send
        
    Returns:
        Response from Telegram API
    """
    token = "2143046655:AAE5iwz9KY8ofLZ_Vm3xhBrjpEyILDYzRy8"  # telegram token
    receiver_id = "-1001512252982"
    return all_send_warp(receiver_id, token, file_path)


def load_questions(file_path: str) -> List[Dict]:
    """Load questions from CSV file.
    
    Args:
        file_path: Path to the questions CSV file
        
    Returns:
        List of question dictionaries
        
    Raises:
        FileNotFoundError: If the CSV file doesn't exist
        ValueError: If CSV is malformed or missing required columns
    """
    if not Path(file_path).exists():
        raise FileNotFoundError(f"Questions file not found: {file_path}")
    
    try:
        df = pd.read_csv(file_path)
        required_columns = ['id', 'question', 'option_A', 'option_B', 
                          'option_C', 'option_D', 'answer']
        
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        return df.to_dict('records')
    except Exception as e:
        raise ValueError(f"Error parsing CSV file: {str(e)}")


def calculate_score(answers: Dict[int, str], questions: List[Dict]) -> int:
    """Calculate score by comparing user answers to correct answers.
    
    Args:
        answers: Dictionary mapping question_id to user's answer (A/B/C/D)
        questions: List of question dictionaries
        
    Returns:
        Number of correct answers
    """
    score = 0
    for question in questions:
        question_id = question['id']
        correct_answer = question['answer']
        user_answer = answers.get(question_id)
        
        if user_answer == correct_answer:
            score += 1
    
    return score


def save_result(file_path: str, user_info: Dict, score: int, total: int):
    """Append quiz result to CSV file.
    
    Args:
        file_path: Path to the results CSV file
        user_info: Dictionary with full_name, permanent_address, facility_address
        score: User's score
        total: Total number of questions
    """
    timestamp = datetime.now().isoformat()
    
    result_data = {
        'timestamp': timestamp,
        'full_name': user_info['full_name'],
        'permanent_address': user_info['permanent_address'],
        'facility_address': user_info['facility_address'],
        'score': score,
        'total_questions': total
    }
    
    df = pd.DataFrame([result_data])
    
    # Append to file (create if doesn't exist)
    df.to_csv(file_path, mode='a', header=not Path(file_path).exists(), index=False)


def save_result_details(file_path: str, user_info: Dict, answers: Dict[int, str], 
                       questions: List[Dict], timestamp: str):
    """Append detailed answer results to CSV file.
    
    Args:
        file_path: Path to the results details CSV file
        user_info: Dictionary with full_name, permanent_address, facility_address
        answers: Dictionary mapping question_id to user's answer (A/B/C/D)
        questions: List of question dictionaries
        timestamp: Timestamp from result submission
    """
    details_rows = []
    
    for question in questions:
        question_id = question['id']
        user_answer = answers.get(question_id, 'Not answered')
        correct_answer = question['answer']
        is_correct = 'Yes' if user_answer == correct_answer else 'No'
        
        detail_row = {
            'timestamp': timestamp,
            'full_name': user_info['full_name'],
            'question_id': question_id,
            'question_text': question['question'],
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct
        }
        details_rows.append(detail_row)
    
    df = pd.DataFrame(details_rows)
    
    # Append to file (create if doesn't exist)
    df.to_csv(file_path, mode='a', header=not Path(file_path).exists(), index=False)
