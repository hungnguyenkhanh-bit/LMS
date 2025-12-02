import requests

# Test login with form data - use student2 who hasn't attempted quiz 5
login_url = 'http://localhost:8000/auth/login'
login_data = {'username': 'student2', 'password': 'password123'}

try:
    response = requests.post(login_url, data=login_data)
    print(f'Login Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        token = data['access_token']
        user = data['user']
        print(f'User: {user["full_name"]} (ID: {user["user_id"]})')
        print(f'Token: {token[:50]}...')
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test 1: Send a message
        print('\n--- Testing Message Send ---')
        msg_url = f'http://localhost:8000/students/{user["user_id"]}/messages'
        msg_data = {'receiver_id': 11, 'content': 'Test message from student2'}
        
        msg_response = requests.post(msg_url, json=msg_data, headers=headers)
        print(f'Message Status: {msg_response.status_code}')
        print(f'Message Response: {msg_response.text[:500]}')
        
        # Test 2: Get quiz details
        print('\n--- Testing Quiz Details ---')
        quiz_url = 'http://localhost:8000/quizzes/5'
        quiz_response = requests.get(quiz_url, headers=headers)
        print(f'Quiz Status: {quiz_response.status_code}')
        if quiz_response.status_code == 200:
            quiz = quiz_response.json()
            print(f'Quiz: {quiz["title"]} (ID: {quiz["id"]})')
            print(f'Questions: {len(quiz.get("questions", []))}')
        
        # Test 3: Start quiz attempt
        print('\n--- Testing Quiz Start ---')
        start_url = 'http://localhost:8000/quizzes/5/start'
        start_response = requests.post(start_url, headers=headers)
        print(f'Start Status: {start_response.status_code}')
        print(f'Start Response: {start_response.text[:500]}')
        
        if start_response.status_code == 200:
            attempt = start_response.json()
            attempt_id = attempt['attempt_id']
            print(f'Attempt ID: {attempt_id}')
            
            # Test 4: Submit quiz with correct question IDs from the quiz
            print('\n--- Testing Quiz Submit ---')
            submit_url = f'http://localhost:8000/quizzes/attempts/{attempt_id}/submit'
            
            # Get actual question IDs from quiz
            question_ids = [q['id'] for q in quiz.get('questions', [])]
            answers = [{'question_id': qid, 'chosen_option': 'A'} for qid in question_ids[:2]]
            
            submit_data = {
                'quiz_id': 5,
                'answers': answers
            }
            print(f'Submit Data: {submit_data}')
            submit_response = requests.post(submit_url, json=submit_data, headers=headers)
            print(f'Submit Status: {submit_response.status_code}')
            print(f'Submit Response: {submit_response.text[:500]}')
    else:
        print(f'Login Error: {response.text}')
except Exception as e:
    import traceback
    print(f'Error: {e}')
    traceback.print_exc()
