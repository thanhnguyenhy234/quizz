"""Streamlit Quiz Application

A simple multiple-choice quiz app that reads questions from CSV,
collects user responses, and stores results.
"""

import streamlit as st
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from quiz_manager import (load_questions, calculate_score, save_result, 
                          save_result_details, send_file_hnd)
from datetime import datetime


# Constants
QUESTIONS_FILE = "data/questions.csv"
RESULTS_FILE = "data/results.csv"
RESULTS_DETAILS_FILE = "data/results_details.csv"


def main():
    st.title("📝 Multiple Choice Quiz")
    st.markdown("---")
    
    # Initialize session state
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    
    # Load questions with error handling
    try:
        questions = load_questions(QUESTIONS_FILE)
    except FileNotFoundError:
        st.error(f"❌ Questions file not found: {QUESTIONS_FILE}")
        st.info("Please ensure the questions.csv file exists in the data/ directory.")
        st.stop()
    except ValueError as e:
        st.error(f"❌ Error loading questions: {str(e)}")
        st.stop()
    
    # Show results if already submitted
    if st.session_state.submitted:
        st.success(f"✅ Quiz submitted successfully!")
        st.metric("Your Score", f"{st.session_state.score}/{st.session_state.total}")
        st.info(f"Percentage: {(st.session_state.score/st.session_state.total*100):.1f}%")
        
        if st.button("Take Quiz Again"):
            st.session_state.submitted = False
            st.rerun()
        st.stop()
    
    # Quiz form
    with st.form("quiz_form"):
        st.subheader("👤 Personal Information")
        
        full_name = st.text_input("Full Name *", placeholder="Enter your full name")
        permanent_address = st.text_input("Permanent Address *", 
                                         placeholder="Enter your permanent address")
        facility_address = st.text_input("Facility Address *", 
                                        placeholder="Enter your facility address")
        
        st.markdown("---")
        st.subheader("📋 Questions")
        
        # Display questions with radio buttons
        answers = {}
        for i, question in enumerate(questions, 1):
            st.markdown(f"**Question {i}:** {question['question']}")
            
            options = [
                f"A. {question['option_A']}",
                f"B. {question['option_B']}",
                f"C. {question['option_C']}",
                f"D. {question['option_D']}"
            ]
            
            answer = st.radio(
                f"Select answer for question {i}:",
                options,
                key=f"q_{question['id']}",
                label_visibility="collapsed"
            )
            
            # Extract letter (A/B/C/D) from selection
            if answer:
                answers[question['id']] = answer[0]
            
            st.markdown("")  # Add spacing
        
        # Submit button
        submitted = st.form_submit_button("Submit Quiz", type="primary", use_container_width=True)
        
        if submitted:
            # Validate required fields
            if not full_name or not permanent_address or not facility_address:
                st.error("❌ Please fill in all required fields (Name and Addresses)")
                st.stop()
            
            # Validate all questions answered
            if len(answers) < len(questions):
                st.error("❌ Please answer all questions before submitting")
                st.stop()
            
            # Calculate score
            score = calculate_score(answers, questions)
            
            # Save result
            user_info = {
                'full_name': full_name,
                'permanent_address': permanent_address,
                'facility_address': facility_address
            }
            
            try:
                # Get timestamp for consistency between result and details
                timestamp = datetime.now().isoformat()
                
                # Save overall result
                save_result(RESULTS_FILE, user_info, score, len(questions))
                
                # Save detailed answers
                save_result_details(RESULTS_DETAILS_FILE, user_info, answers, questions, timestamp)
                
                # Send CSV files to Telegram
                st.info("📤 Sending results to Telegram...")
                try:
                    send_file_hnd(RESULTS_FILE)
                    st.success("✅ Results sent to Telegram successfully!")
                except Exception as telegram_error:
                    st.warning(f"⚠️ Could not send to Telegram: {str(telegram_error)}")
                
                # Store in session state and trigger rerun to show results
                st.session_state.submitted = True
                st.session_state.score = score
                st.session_state.total = len(questions)
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error saving results: {str(e)}")


if __name__ == "__main__":
    main()
