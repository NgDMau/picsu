import openpyxl
import random
import django
import os

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'picsu.settings')  # Replace 'your_project.settings' with your actual Django project's settings
# django.setup()

from study.models import UserTestResponse, UserTestScore
from django.contrib.auth.models import User
from datetime import timedelta
from user.models import UserProfile

WINDOW_TIME= 1 # (in seconds)
PICSU_MAX_QUESTS = 60
FLASHCARD_MAX_QUESTS = 80

def max_quests(test_type):
    if test_type == "first_test_picsu" or test_type == "retention_test_picsu":
        return 60
    elif test_type == "first_test_flashcard" or test_type == "retention_test_flashcard":
        return 80
    else:
        return 999

def group_test_responses():
    all_user_results = {}
    print("Geting all uses results...")
    for user in User.objects.all():
        # Fetch all responses for the user
        responses = UserTestResponse.objects.filter(user=user).select_related('user', 'question').prefetch_related('correct_answers', 'user_answers').order_by("test_date")

        print("Getting all responses")
        current_test_responses = []
        current_test_start_time = None

        for response in responses:
            if (not current_test_start_time or (response.test_date - current_test_start_time <= timedelta(minutes=WINDOW_TIME))):
                current_test_responses.append(response)
                if not current_test_start_time:
                    current_test_start_time = response.test_date
            else:
                result = process_test_group(user, current_test_responses)
                if result:
                    # Append the result to this user's results in all_user_results
                    if user.username not in all_user_results:
                        all_user_results[user.username] = []
                    all_user_results[user.username].append(result)

                current_test_responses = [response]
                current_test_start_time = response.test_date

        # Don't forget to process the last group
        if current_test_responses:
            result = process_test_group(user, current_test_responses)
            if result:
                if user.username not in all_user_results:
                    all_user_results[user.username] = []
                all_user_results[user.username].append(result)

    return all_user_results


def process_test_group(user, responses):
    print(f"Processing for user {user.username}")
    # Assuming the first response's test_date represents the start of the test
    test_start_time = responses[0].test_date

    # Find the UserTestScore that corresponds to this test
    # Adjust the timedelta if needed to better match how your tests are separated
    test_score = UserTestScore.objects.filter(
        user=user,
        test_date__range=(test_start_time, test_start_time + timedelta(minutes=WINDOW_TIME))
    ).first()

    if test_score:
        user_profile = UserProfile.objects.get(user=user)

        dictionary = "Unknown"  # Default value
        if "picsu" in test_score.type.lower() and user_profile.picsu_dict:
            dictionary = user_profile.picsu_dict.upper()
        elif "flashcard" in test_score.type.lower() and user_profile.flashcard_dict:
            dictionary = user_profile.flashcard_dict.upper()

        total_questions = len(responses)        
        questions_with_correct_answer = 0
        total_possible_correct_answers = 0
        total_answers_chosen = 0
        total_actual_correct_answers = 0
        total_false_positives = 0

        for response in responses:
            correct_answers_set = set(response.correct_answers.all())
            user_answers_set = set(response.user_answers.all())
            
            correct_selected = correct_answers_set & user_answers_set
            incorrect_selected = user_answers_set - correct_answers_set
            
            questions_with_correct_answer += (1 if correct_selected else 0)
            total_possible_correct_answers += len(correct_answers_set)
            total_answers_chosen += len(user_answers_set)
            total_actual_correct_answers += len(correct_selected)
            total_false_positives += len(incorrect_selected)
        
        print("DONE COLLECTING METRICS")

        print(f"Processing data for user {user.username}")
        result = {
            'user': user.username,
            'test_type': test_score.type,
            'dictionary': dictionary,
            'test_start_time': test_start_time,
            'total_questions': total_questions,
            'max_questions': max_quests(test_score.type),
            'questions_with_correct_answer': questions_with_correct_answer,
            'total_possible_correct_answers': total_possible_correct_answers,
            'total_answers_chosen': total_answers_chosen,
            'total_actual_correct_answers': total_actual_correct_answers,
            'total_false_positives': total_false_positives,
        }
        return result
    else:
        print(f"No matching UserTestScore found for User: {user.username}, Test on: {test_start_time}")
        return None
    

if __name__ == "__main__":
    # Run the grouping function
    group_test_responses()