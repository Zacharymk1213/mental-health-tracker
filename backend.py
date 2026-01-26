import sqlite3
from datetime import datetime

def calculate_burns_score(responses):
    """
    Calculate total score from array of 25 responses
    Each response should be between 0-4
    """
    if len(responses) != 25:
        raise ValueError("Must provide exactly 25 responses")
        
    if not all(isinstance(x, int) and 0 <= x <= 4 for x in responses):
        raise ValueError("All responses must be integers between 0 and 4")
        
    return sum(responses)

def get_depression_level(score):
    """
    Return depression level based on total score
    """
    if 0 <= score <= 5:
        return "No Depression"
    elif 6 <= score <= 10:
        return "Normal but unhappy"
    elif 11 <= score <= 25:
        return "Mild depression"
    elif 26 <= score <= 50:
        return "Moderate depression"
    elif 51 <= score <= 75:
        return "Severe depression"
    elif 76 <= score <= 100:
        return "Extreme depression"
    else:
        return "Invalid score"

def calculate_gad7_score(responses):
    """
    Calculate total score from array of 7 responses
    Each response should be between 0-3
    """
    if len(responses) != 7:
        raise ValueError("Must provide exactly 7 responses")
        
    if not all(isinstance(x, int) and 0 <= x <= 3 for x in responses):
        raise ValueError("All responses must be integers between 0 and 3")
        
    return sum(responses)

def get_anxiety_level(score):
    """
    Return anxiety level based on GAD-7 score
    """
    if 0 <= score <= 4:
        return "Minimal anxiety"
    elif 5 <= score <= 9:
        return "Mild anxiety"
    elif 10 <= score <= 14:
        return "Moderate anxiety"
    elif 15 <= score <= 21:
        return "Severe anxiety"
    else:
        return "Invalid score"

def init_db():
    """
    Initialize SQLite database and create tables if they don't exist
    """
    conn = sqlite3.connect('mental_health_checklist.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS checklist_entries
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         score INTEGER NOT NULL,
         depression_level TEXT NOT NULL,
         timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS gad7_entries
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         score INTEGER NOT NULL,
         anxiety_level TEXT NOT NULL,
         timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
    ''')
    conn.commit()
    conn.close()

def save_score(score):
    """
    Save Burns score to database with current timestamp
    Returns the entry ID
    """
    conn = sqlite3.connect('mental_health_checklist.db')
    c = conn.cursor()
    
    depression_level = get_depression_level(score)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    c.execute('''
        INSERT INTO checklist_entries (score, depression_level, timestamp)
        VALUES (?, ?, ?)
    ''', (score, depression_level, current_time))
    
    entry_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return entry_id

def get_all_entries():
    """
    Retrieve all Burns entries from database
    """
    conn = sqlite3.connect('mental_health_checklist.db')
    c = conn.cursor()
    c.execute('SELECT * FROM checklist_entries ORDER BY timestamp DESC')
    entries = c.fetchall()
    conn.close()
    return entries

def save_gad7_score(score):
    """
    Save GAD-7 score to database with current timestamp
    Returns the entry ID
    """
    conn = sqlite3.connect('mental_health_checklist.db')
    c = conn.cursor()
    
    anxiety_level = get_anxiety_level(score)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    c.execute('''
        INSERT INTO gad7_entries (score, anxiety_level, timestamp)
        VALUES (?, ?, ?)
    ''', (score, anxiety_level, current_time))
    
    entry_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return entry_id

def get_all_gad7_entries():
    """
    Retrieve all GAD-7 entries from database
    """
    conn = sqlite3.connect('mental_health_checklist.db')
    c = conn.cursor()
    c.execute('SELECT * FROM gad7_entries ORDER BY timestamp DESC')
    entries = c.fetchall()
    conn.close()
    return entries

# Initialize database when module is imported
init_db()

# Example usage:
if __name__ == "__main__":
    # Example Burns checklist responses
    sample_burns_responses = [2, 1, 0, 2, 1, 3, 2, 1, 0, 2, 1, 0, 2, 1, 3, 
                              2, 1, 0, 2, 1, 0, 2, 1, 0, 0]
    
    # Calculate Burns score
    burns_score = calculate_burns_score(sample_burns_responses)
    print(f"Total Burns Score: {burns_score}")
    print(f"Depression Level: {get_depression_level(burns_score)}")
    
    # Save Burns score to database
    burns_entry_id = save_score(burns_score)
    print(f"Saved Burns entry with ID: {burns_entry_id}")
    
    # Retrieve all Burns entries
    burns_entries = get_all_entries()
    print("\nAll Burns entries:")
    for entry in burns_entries:
        print(f"ID: {entry[0]}, Score: {entry[1]}, Level: {entry[2]}, Time: {entry[3]}")
        
    print("-" * 20)

    # Example GAD-7 responses
    sample_gad7_responses = [1, 2, 3, 2, 1, 0, 1]
    
    # Calculate GAD-7 score
    gad7_score = calculate_gad7_score(sample_gad7_responses)
    print(f"Total GAD-7 Score: {gad7_score}")
    print(f"Anxiety Level: {get_anxiety_level(gad7_score)}")
    
    # Save GAD-7 score to database
    gad7_entry_id = save_gad7_score(gad7_score)
    print(f"Saved GAD-7 entry with ID: {gad7_entry_id}")
    
    # Retrieve all GAD-7 entries
    gad7_entries = get_all_gad7_entries()
    print("\nAll GAD-7 entries:")
    for entry in gad7_entries:
        print(f"ID: {entry[0]}, Score: {entry[1]}, Level: {entry[2]}, Time: {entry[3]}")
