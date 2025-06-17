import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
import streamlit as st

def analyze_user_progress(skill_sessions: List[Dict], prompt_sessions: List[Dict]) -> Dict[str, Any]:
    """
    Analyze user progress based on skill sessions and prompt sessions data.
    
    Args:
        skill_sessions: List of skill session records from Coda
        prompt_sessions: List of prompt session records from Coda
    
    Returns:
        Dictionary containing progress analysis
    """
    if not skill_sessions:
        return {
            'total_sessions': 0,
            'average_score': 0,
            'skill_progress': {},
            'trends': {},
            'recommendations': ['Start practicing to build your learning history!']
        }
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(skill_sessions)
    
    # Clean and convert skill_score to numeric
    if 'skill_score' in df.columns:
        # Convert to numeric, coercing errors to NaN
        df['skill_score'] = pd.to_numeric(df['skill_score'], errors='coerce')
        # Remove rows with NaN scores
        df = df.dropna(subset=['skill_score'])
    
    # Basic statistics
    total_sessions = len(prompt_sessions) if prompt_sessions else 0
    average_score = df['skill_score'].mean() if 'skill_score' in df.columns and not df.empty else 0
    
    # Skill-specific progress
    skill_progress = {}
    if 'Skill' in df.columns and 'skill_score' in df.columns and not df.empty:
        for skill in df['Skill'].unique():
            skill_data = df[df['Skill'] == skill]
            if len(skill_data) > 0:
                skill_progress[skill] = {
                    'average_score': skill_data['skill_score'].mean(),
                    'total_attempts': len(skill_data),
                    'latest_score': skill_data['skill_score'].iloc[-1] if len(skill_data) > 0 else 0,
                    'improvement': skill_data['skill_score'].iloc[-1] - skill_data['skill_score'].iloc[0] if len(skill_data) > 1 else 0
                }
    
    # Analyze trends (last 7 days vs previous 7 days)
    trends = analyze_trends(df, prompt_sessions)
    
    # Generate recommendations
    recommendations = generate_recommendations(skill_progress, trends, total_sessions)
    
    return {
        'total_sessions': total_sessions,
        'average_score': round(average_score, 1),
        'skill_progress': skill_progress,
        'trends': trends,
        'recommendations': recommendations
    }

def analyze_trends(skill_df: pd.DataFrame, prompt_sessions: List[Dict]) -> Dict[str, Any]:
    """
    Analyze trends in user performance over time.
    """
    if skill_df.empty or not prompt_sessions:
        return {'recent_performance': 'No data available', 'trend_direction': 'neutral'}
    
    # Convert date strings to datetime
    try:
        skill_df['date_time'] = pd.to_datetime(skill_df['date_time'], errors='coerce')
        # Remove rows with invalid dates
        skill_df = skill_df.dropna(subset=['date_time'])
        
        if skill_df.empty:
            return {'recent_performance': 'No valid date data', 'trend_direction': 'neutral'}
        
        recent_cutoff = datetime.now() - timedelta(days=7)
        
        recent_scores = skill_df[skill_df['date_time'] >= recent_cutoff]['skill_score'].mean()
        older_scores = skill_df[skill_df['date_time'] < recent_cutoff]['skill_score'].mean()
        
        if pd.isna(recent_scores) or pd.isna(older_scores):
            return {'recent_performance': 'Insufficient data', 'trend_direction': 'neutral'}
        
        improvement = recent_scores - older_scores
        
        if improvement > 5:
            trend_direction = 'improving'
            recent_performance = f"Great progress! Your recent average score is {recent_scores:.1f}"
        elif improvement < -5:
            trend_direction = 'declining'
            recent_performance = f"Your recent average score is {recent_scores:.1f}. Consider reviewing previous sessions."
        else:
            trend_direction = 'stable'
            recent_performance = f"Your performance is stable with an average score of {recent_scores:.1f}"
            
    except Exception as e:
        return {'recent_performance': 'Unable to analyze trends', 'trend_direction': 'neutral'}
    
    return {
        'recent_performance': recent_performance,
        'trend_direction': trend_direction,
        'recent_average': round(recent_scores, 1) if not pd.isna(recent_scores) else 0,
        'improvement': round(improvement, 1) if not pd.isna(improvement) else 0
    }

def generate_recommendations(skill_progress: Dict, trends: Dict, total_sessions: int) -> List[str]:
    """
    Generate personalized learning recommendations based on progress analysis.
    """
    recommendations = []
    
    # Session frequency recommendations
    if total_sessions < 3:
        recommendations.append("🎯 **Start Strong**: Aim for at least 3 practice sessions this week to build momentum.")
    elif total_sessions < 10:
        recommendations.append("📈 **Build Consistency**: Great start! Try to practice 2-3 times per week for steady improvement.")
    else:
        recommendations.append("🏆 **Maintain Excellence**: You're on a great track! Keep up the regular practice routine.")
    
    # Skill-specific recommendations
    weak_skills = []
    strong_skills = []
    
    for skill, progress in skill_progress.items():
        if progress['average_score'] < 60:
            weak_skills.append(skill)
        elif progress['average_score'] > 80:
            strong_skills.append(skill)
    
    if weak_skills:
        recommendations.append(f"🎯 **Focus Areas**: Prioritize practice on: {', '.join(weak_skills[:3])}")
    
    if strong_skills:
        recommendations.append(f"💪 **Strengths**: You're excelling in: {', '.join(strong_skills[:2])}")
    
    # Trend-based recommendations
    if trends.get('trend_direction') == 'declining':
        recommendations.append("📚 **Review Time**: Consider revisiting previous sessions to reinforce learning.")
    elif trends.get('trend_direction') == 'improving':
        recommendations.append("🚀 **Keep Momentum**: Your recent improvement is excellent! Maintain this pace.")
    
    # General learning tips
    if len(recommendations) < 4:
        recommendations.append("💡 **Pro Tip**: Practice speaking at a natural pace and focus on clear pronunciation.")
    
    return recommendations

def get_learning_goals(username: str, skill_progress: Dict) -> List[Dict[str, Any]]:
    """
    Generate personalized learning goals based on current skill levels.
    """
    goals = []
    
    # Overall fluency goal
    fluency_progress = skill_progress.get('Fluency (WPM)', {})
    current_wpm = fluency_progress.get('average_score', 0)
    
    if current_wpm < 100:
        goals.append({
            'skill': 'Fluency (WPM)',
            'current': current_wpm,
            'target': min(current_wpm + 20, 120),
            'timeframe': '2 weeks',
            'description': f'Increase speaking rate from {current_wpm} to {min(current_wpm + 20, 120)} WPM'
        })
    
    # Skill-specific goals
    for skill, progress in skill_progress.items():
        if skill == 'Fluency (WPM)':
            continue
            
        current_score = progress.get('average_score', 0)
        if current_score < 70:
            goals.append({
                'skill': skill,
                'current': current_score,
                'target': min(current_score + 15, 85),
                'timeframe': '3 weeks',
                'description': f'Improve {skill} from {current_score:.0f} to {min(current_score + 15, 85):.0f}'
            })
    
    # Add a general goal if not enough specific ones
    if len(goals) < 2:
        goals.append({
            'skill': 'Overall Performance',
            'current': sum(p.get('average_score', 0) for p in skill_progress.values()) / max(len(skill_progress), 1),
            'target': 80,
            'timeframe': '1 month',
            'description': 'Achieve an overall average score of 80+ across all skills'
        })
    
    return goals

def format_progress_data(progress_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format progress data for display in the My Progress UI.
    """
    formatted = {
        'summary': {
            'total_sessions': progress_data.get('total_sessions', 0),
            'average_score': progress_data.get('average_score', 0),
            'trend': progress_data.get('trends', {}).get('trend_direction', 'neutral')
        },
        'skills': [],
        'goals': get_learning_goals('user', progress_data.get('skill_progress', {})),
        'recommendations': progress_data.get('recommendations', [])
    }
    
    # Format skill data
    for skill, data in progress_data.get('skill_progress', {}).items():
        formatted['skills'].append({
            'name': skill,
            'average_score': round(data.get('average_score', 0), 1),
            'total_attempts': data.get('total_attempts', 0),
            'improvement': round(data.get('improvement', 0), 1),
            'status': 'improving' if data.get('improvement', 0) > 0 else 'stable' if data.get('improvement', 0) == 0 else 'needs_attention'
        })
    
    return formatted 