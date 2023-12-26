import openpyxl
import random
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'picsu.settings')  # Replace 'your_project.settings' with your actual Django project's settings
django.setup()

from study.models import Word, Answer, Question, UserTestResponse, UserTestScore
from django.contrib.auth.models import User
from datetime import timedelta

WINDOW_TIME=1 # (in seconds)
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
    for user in User.objects.all():
        # Fetch all responses for the user
        responses = UserTestResponse.objects.filter(user=user).order_by('test_date')

        current_test_responses = []
        current_test_start_time = None

        for response in responses:

            if (not current_test_start_time or response.test_date - current_test_start_time <= timedelta(minutes=WINDOW_TIME)):
                # This response is part of the current test
                current_test_responses.append(response)
                if not current_test_start_time:
                    current_test_start_time = response.test_date
            else:
                # This response is part of a new test
                process_test_group(user, current_test_responses)

                current_test_responses = [response]
                current_test_start_time = response.test_date

        # Don't forget to process the last group
        if current_test_responses:
            process_test_group(user, current_test_responses)



def process_test_group(user, responses):
    # Assuming the first response's test_date represents the start of the test
    test_start_time = responses[0].test_date

    # Find the UserTestScore that corresponds to this test
    # Adjust the timedelta if needed to better match how your tests are separated
    test_score = UserTestScore.objects.filter(
        user=user,
        test_date__range=(test_start_time, test_start_time + timedelta(minutes=WINDOW_TIME))
    ).first()

    if test_score:
        total_questions = len(responses)
        questions_with_correct_answer = 0

        for response in responses:
            # Check if the user has selected at least one correct answer for the question
            if set(response.correct_answers.all()) & set(response.user_answers.all()):
                questions_with_correct_answer += 1

        total_possible_correct_answers = sum([response.question.correct_answers.count() for response in responses])
        total_answers_chosen = sum([len(response.user_answers.all()) for response in responses])
        total_actual_correct_answers = sum([len(set(response.correct_answers.all()) & set(response.user_answers.all())) for response in responses if set(response.correct_answers.all()) & set(response.user_answers.all())])
        total_false_positives = sum([len(set(response.user_answers.all()) - set(response.correct_answers.all())) for response in responses])

        
        # Decorated printing
        print("-" * 80)  # Print a separator line
        print(f"User: {user.username} | Test on: {test_start_time} | Test Type: {test_score.type}")
        print(f"Questions with at least one correct answer: {questions_with_correct_answer} out of {total_questions} (max {max_quests(test_score.type)})")
        print(f"Participant's Correct Answers: {total_actual_correct_answers} out of {total_answers_chosen} out of {total_possible_correct_answers}")
        print(f"XXX Participant's Incorrect Answers: {total_false_positives} out of {total_answers_chosen} out of {total_possible_correct_answers}")
        print(f"Total Answers Chosen: {test_score.total_answers_chosen} | Total Correct Answers: {test_score.correct_answers_count} | Total Incorrect Answers: {test_score.incorrect_answers_count}")
        print("-" * 80)  # End with another separator line
    else:
        print(f"No matching UserTestScore found for User: {user.username}, Test on: {test_start_time}")


if __name__ == "__main__":
    # Run the grouping function
    group_test_responses()