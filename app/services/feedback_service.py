def process_feedback(feedback):
    
    # Mock storage: logging the feedback
    print(f"[STORAGE] Saving feedback for ID {feedback.get('transformation_id')}: "
          f"Rating={feedback.get('rating')}, Comments='{feedback.get('comments')}'")
    return True
