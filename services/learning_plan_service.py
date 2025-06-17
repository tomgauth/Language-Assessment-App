import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random
from codaio import Coda, Document
import os
from dotenv import load_dotenv
import numpy as np

# Load environment variables
load_dotenv()

# Initialize Coda client
coda = Coda(os.getenv("CODA_API_KEY"))

# Demo document and table IDs
DEMO_DOC_ID = "jPJTMi7bJR"
DEMO_USERS_TABLE = "grid-LJUorNwMyd"

def get_table_rows(doc_id: str, table_id: str):
    """Get all rows from a Coda table"""
    coda = Coda(os.getenv("CODA_API_KEY"))
    doc = Document(doc_id, coda=coda)
    table = doc.get_table(table_id)
    rows = table.rows()
    return [row.to_dict() for row in rows]

def get_user_learning_data(username: str) -> Dict[str, Any]:
    """
    Fetch user learning data from the Demo Users table.
    
    Args:
        username: The username to fetch data for
    
    Returns:
        Dictionary containing user learning data
    """
    try:
        doc = Document(DEMO_DOC_ID, coda=coda)
        table = doc.get_table(DEMO_USERS_TABLE)
        rows = table.rows()
        
        # Find the user row
        user_row = None
        for row in rows:
            row_data = row.to_dict()
            if row_data.get('username') == username:
                user_row = row_data
                break
        
        if not user_row:
            return None
            
        return {
            'demo_conversation': user_row.get('demo_conversation', ''),
            'demo_topics': user_row.get('demo_topics', ''),
            'demo_skills': user_row.get('demo_skills', ''),
            'prompts': user_row.get('prompts', ''),
            'num_sentence_recall': user_row.get('num_sentence_recall', 0),
            'num_sentences_recognize': user_row.get('num_sentences_recognize', 0)
        }
    except Exception as e:
        print(f"Error fetching user data: {e}")
        return None

def generate_learning_plan_data(username: str) -> Dict[str, Any]:
    """
    Generate comprehensive learning plan data for a user based on demo users table.
    
    Args:
        username: Username to generate plan for
    
    Returns:
        Dictionary containing all learning plan data
    """
    # Get user data from demo users table
    rows = get_table_rows(DEMO_DOC_ID, DEMO_USERS_TABLE)
    user_row = next((row for row in rows if row.get('username') == username), None)
    
    if not user_row:
        # Return default data if user not found
        return get_default_learning_plan_data()
    
    # Extract user data using the proper field structure
    conversation_type = user_row.get('demo_conversation', 'General Conversation')
    topics = user_row.get('demo_topics', '')
    skills = user_row.get('demo_skills', '')
    prompts = user_row.get('prompts', '')
    program_duration = user_row.get('program_duration', 90)
    current_wpm = user_row.get('current_wpm', 60)
    num_sentence_recall = user_row.get('num_sentence_recall', 350)
    num_sentences_recognize = user_row.get('num_sentences_recognize', 700)
    start_date = user_row.get('start_date', '')
    target_wpm = user_row.get('target_wpm', 100)
    
    # Parse topics and skills
    topic_list = [topic.strip() for topic in topics.split(',') if topic.strip()] if topics else ['General Topics']
    skill_list = [skill.strip() for skill in skills.split(',') if skill.strip()] if skills else ['Basic Communication']
    prompt_list = [prompt.strip() for prompt in prompts.split(',') if prompt.strip()] if prompts else []
    
    # Estimate sentences per topic and skill
    topic_sentences = estimate_sentences_per_topic(topic_list, num_sentence_recall, num_sentences_recognize)
    skill_sentences = estimate_sentences_per_skill(skill_list, num_sentence_recall, num_sentences_recognize)
    
    # Generate learning plan data
    learning_data = {
        'conversation_type': conversation_type,
        'difficulty': 'Intermediate',
        'learning_days': program_duration,
        'sentences_to_recall': num_sentence_recall,
        'sentences_to_recognize': num_sentences_recognize,
        'total_sentences': num_sentence_recall + num_sentences_recognize,
        'traditional_speed': 3,  # sentences per day traditional
        'fsrs_speed': 10.5,  # sentences per day with FSRS (3.5x improvement)
        'new_sentences_per_day': 12,  # new sentences per day
        'expected_sentences_known': num_sentence_recall + num_sentences_recognize,
        'expected_final_wpm': target_wpm,
        'current_wpm': current_wpm,
        'fluency_improvement': target_wpm - current_wpm,
        'start_date': start_date
    }
    
    # User information
    user_info = {
        'username': username,
        'current_level': 'B1',  # Current level B1
        'current_wpm': current_wpm,
        'conversation_type': conversation_type,
        'total_days': program_duration,
        'target_level': 'B2+',
        'target_wpm': target_wpm,
        'start_date': start_date
    }
    
    # Content breakdown
    content = {
        'topics': topic_list,
        'skills': skill_list,
        'prompts': prompt_list,
        'topic_sentences': topic_sentences,
        'skill_sentences': skill_sentences,
        'total_hours': program_duration * 1.5,  # 1.5 hours per day
        'sessions_per_week': 7,
        'hours_per_session': 1.5
    }
    
    # Methodology comparison
    methodology_comparison = {
        'learning_speed': {
            'traditional': 3,
            'our_method': 10.5,
            'improvement': 3.5
        },
        'learning_volume': {
            'traditional': (num_sentence_recall + num_sentences_recognize) // 4,
            'our_method': num_sentence_recall + num_sentences_recognize,
            'improvement': 4.0
        },
        'fluency_impact': {
            'traditional': 20,
            'our_method': target_wpm - current_wpm,
            'improvement': 2.0
        },
        'comprehension_impact': {
            'traditional': 1,
            'improvement': 2.5
        }
    }
    
    # Generate milestones
    milestones = generate_milestones(learning_data)
    
    # Generate learning summary
    learning_summary = generate_learning_summary(user_info, learning_data, content)
    
    return {
        'user_info': user_info,
        'learning_data': learning_data,
        'content': content,
        'methodology_comparison': methodology_comparison,
        'milestones': milestones,
        'learning_summary': learning_summary
    }

def estimate_sentences_per_topic(topics: List[str], total_recall: int, total_recognize: int) -> Dict[str, Dict[str, int]]:
    """
    Estimate the number of sentences per topic based on topic complexity and importance.
    
    Args:
        topics: List of topics
        total_recall: Total recall sentences
        total_recognize: Total recognition sentences
    
    Returns:
        Dictionary with topic breakdown
    """
    if not topics:
        return {}
    
    # Define topic weights based on complexity and importance
    topic_weights = {
        '💼 Previous work experience': 0.25,
        '🎯 Why I\'m applying for the job': 0.20,
        '🪞 My strengths and weaknesses': 0.15,
        'General Topics': 0.10
    }
    
    # Calculate sentences per topic
    topic_sentences = {}
    for topic in topics:
        # Get weight for this topic, default to 0.10 if not found
        weight = topic_weights.get(topic, 0.10)
        
        # Calculate sentences for this topic
        recall_sentences = int(total_recall * weight)
        recognize_sentences = int(total_recognize * weight)
        
        topic_sentences[topic] = {
            'recall_sentences': recall_sentences,
            'recognize_sentences': recognize_sentences,
            'total_sentences': recall_sentences + recognize_sentences
        }
    
    return topic_sentences

def estimate_sentences_per_skill(skills: List[str], total_recall: int, total_recognize: int) -> Dict[str, Dict[str, int]]:
    """
    Estimate the number of sentences per skill based on skill complexity and importance.
    
    Args:
        skills: List of skills
        total_recall: Total recall sentences
        total_recognize: Total recognition sentences
    
    Returns:
        Dictionary with skill breakdown
    """
    if not skills:
        return {}
    
    # Define skill weights based on complexity and importance
    skill_weights = {
        '🧾 Use professional and precise vocabulary': 0.30,
        '💪 Show confidence in French': 0.25,
        '🎓 Understand and apply French interview etiquette': 0.20,
        'Basic Communication': 0.10
    }
    
    # Calculate sentences per skill
    skill_sentences = {}
    for skill in skills:
        # Get weight for this skill, default to 0.10 if not found
        weight = skill_weights.get(skill, 0.10)
        
        # Calculate sentences for this skill
        recall_sentences = int(total_recall * weight)
        recognize_sentences = int(total_recognize * weight)
        
        skill_sentences[skill] = {
            'recall_sentences': recall_sentences,
            'recognize_sentences': recognize_sentences,
            'total_sentences': recall_sentences + recognize_sentences
        }
    
    return skill_sentences

def format_learning_plan_for_display(plan_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format learning plan data for display in the UI.
    """
    return {
        'user_info': plan_data['user_info'],
        'learning_data': plan_data['learning_data'],
        'content': plan_data['content'],
        'methodology_comparison': plan_data['methodology_comparison'],
        'milestones': plan_data['milestones'],
        'learning_summary': plan_data['learning_summary']
    }

def generate_90_day_progress_data(learning_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate 90-day progress projection data with S-curves for different learning metrics.
    
    Args:
        learning_data: Learning data containing target values and parameters
    
    Returns:
        Dictionary containing daily progress data for 90 days
    """
    # Target values
    target_recall = learning_data['sentences_to_recall']
    target_recognize = learning_data['sentences_to_recognize']
    target_fluency = learning_data['expected_final_wpm']
    target_communication = 95  # Target communication skills score
    
    # Starting values
    start_fluency = 60  # Starting WPM (B1 level)
    start_communication = 30  # Starting communication score
    
    # Generate 90 days of data
    days = list(range(1, 91))
    
    # Base S-curve data (the same pattern for all curves)
    base_s_curve_data = [
        0, 0, 0, 1, 1, 1, 1, 1, 1, 1,
        2, 2, 2, 2, 3, 3, 4, 5, 5, 6,
        7, 8, 10, 12, 13, 16, 18, 21, 24, 28,
        32, 37, 43, 49, 56, 64, 73, 82, 93, 104,
        116, 128, 141, 154, 168, 182, 196, 209, 222, 234,
        246, 257, 268, 277, 286, 294, 301, 307, 313, 318,
        322, 326, 329, 332, 334, 337, 338, 340, 342, 343,
        344, 345, 345, 346, 347, 347, 348, 348, 348, 348,
        349, 349, 349, 349, 349, 349, 349, 350, 350, 350
    ]
    
    # Scale the base data for each metric
    recall_scale = target_recall / 350.0
    recognize_scale = target_recognize / 350.0
    fluency_scale = (target_fluency - start_fluency) / 350.0
    communication_scale = (target_communication - start_communication) / 350.0
    
    # Generate data for each metric using the same S-curve pattern
    recall_data = [round(val * recall_scale, 1) for val in base_s_curve_data]
    recognize_data = [round(val * recognize_scale, 1) for val in base_s_curve_data]
    fluency_data = [round(start_fluency + val * fluency_scale, 1) for val in base_s_curve_data]
    communication_data = [round(start_communication + val * communication_scale, 1) for val in base_s_curve_data]
    
    return {
        'days': days,
        'recall_sentences': recall_data,
        'recognize_sentences': recognize_data,
        'fluency_wpm': fluency_data,
        'communication_skills': communication_data,
        'targets': {
            'recall': target_recall,
            'recognize': target_recognize,
            'fluency': target_fluency,
            'communication': target_communication
        }
    }

def get_default_learning_plan_data() -> Dict[str, Any]:
    """Return default learning plan data when user is not found"""
    user_info = {
        'username': 'Demo User',
        'current_level': 'B1',
        'current_wpm': 60,
        'conversation_type': 'General Conversation',
        'total_days': 90,
        'target_level': 'B2+',
        'target_wpm': 100
    }
    learning_data = {
        'conversation_type': 'General Conversation',
        'difficulty': 'Intermediate',
        'learning_days': 90,
        'sentences_to_recall': 350,
        'sentences_to_recognize': 700,
        'total_sentences': 1050,
        'traditional_speed': 3,
        'fsrs_speed': 10.5,
        'new_sentences_per_day': 12,
        'expected_sentences_known': 1050,
        'expected_final_wpm': 100,
        'current_wpm': 60,
        'fluency_improvement': 40
    }
    content = {
        'topics': ['General Topics'],
        'skills': ['Basic Communication'],
        'total_hours': 135,
        'sessions_per_week': 7,
        'hours_per_session': 1.5
    }
    return {
        'user_info': user_info,
        'learning_data': learning_data,
        'content': content,
        'methodology_comparison': {
            'learning_speed': {
                'traditional': 3,
                'our_method': 10.5,
                'improvement': 3.5
            },
            'learning_volume': {
                'traditional': 270,
                'our_method': 1050,
                'improvement': 3.9
            },
            'fluency_impact': {
                'traditional': 20,
                'our_method': 40,
                'improvement': 2.0
            },
            'comprehension_impact': {
                'traditional': 1,
                'improvement': 2.5
            }
        },
        'milestones': generate_milestones({
            'learning_days': 90,
            'sentences_to_recall': 350,
            'sentences_to_recognize': 700,
            'expected_final_wpm': 100
        }),
        'learning_summary': generate_learning_summary(
            user_info,
            learning_data,
            content
        )
    }

def generate_milestones(learning_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate learning milestones based on learning data"""
    from datetime import datetime, timedelta
    
    current_date = datetime.now()
    learning_days = learning_data['learning_days']
    
    milestones = [
        {
            'date': current_date + timedelta(days=learning_days // 3),
            'milestone': 'Complete Foundation Phase',
            'description': f'Master {learning_data["sentences_to_recall"] // 3} recall sentences and {learning_data["sentences_to_recognize"] // 3} recognition sentences'
        },
        {
            'date': current_date + timedelta(days=learning_days * 2 // 3),
            'milestone': 'Complete Intermediate Phase',
            'description': f'Master {learning_data["sentences_to_recall"] * 2 // 3} recall sentences and {learning_data["sentences_to_recognize"] * 2 // 3} recognition sentences'
        },
        {
            'date': current_date + timedelta(days=learning_days),
            'milestone': 'Complete Advanced Program',
            'description': f'Expected to know {learning_data["sentences_to_recall"] + learning_data["sentences_to_recognize"]} sentences and achieve {learning_data["expected_final_wpm"]} WPM fluency'
        }
    ]
    
    return milestones

def generate_learning_summary(user_info: Dict[str, Any], learning_data: Dict[str, Any], content: Dict[str, Any]) -> str:
    """Generate learning plan summary text"""
    return f"""
    **Personalized Learning Plan for {user_info['username']}**
    
    **Program Overview:**
    - **Duration:** {user_info['total_days']} days
    - **Current Level:** {user_info['current_level']}
    - **Current Fluency:** {user_info['current_wpm']} WPM
    - **Conversation Type:** {user_info['conversation_type']}
    
    **Learning Objectives:**
    - Master {learning_data['sentences_to_recall']} sentences for active recall
    - Recognize {learning_data['sentences_to_recognize']} sentences passively
    - Achieve {learning_data['expected_final_wpm']} WPM fluency
    - Develop {len(content['skills'])} key language skills
    
    **Our Advanced Methodology:**
    - **FSRS Algorithm:** Machine learning increases learning speed by 3.5x compared to conventional methods
    - **Audio Comprehension:** Incredible impact on comprehension and practice speed
    - **Fluency Analyzer:** 2x impact on fluency (typically 60 WPM at B1 to 100 WPM after practice)
    - **DIRECT Method:** High impact on communication and confidence with trained teachers
    
    **Expected Outcomes:**
    By the end of this program, you'll be able to confidently engage in {user_info['conversation_type'].lower()} conversations, 
    with fluency improving from {user_info['current_wpm']} to {learning_data['expected_final_wpm']} WPM.
    """ 