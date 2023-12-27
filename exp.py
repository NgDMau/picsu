import openpyxl
import random
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'picsu.settings')  # Replace 'your_project.settings' with your actual Django project's settings
django.setup()

from study.models import Word, Answer, Question, UserTestResponse, UserTestScore
from django.contrib.auth.models import User
from django.db import IntegrityError

from datetime import timedelta

import csv
from study.models import UserTestResponse

# Function to export UserTestResponse data
def export_user_test_responses():
    with open('study_usertestresponse.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        # Write headers
        writer.writerow(['ID', 'User ID', 'Question ID', 'Test Date'])
        # Write data rows
        for utr in UserTestResponse.objects.all():
            writer.writerow([utr.id, utr.user_id, utr.question_id, utr.test_date])

# Function to export correct answers data
def export_correct_answers():
    with open('study_usertestresponse_correct_answers.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        # Write headers
        writer.writerow(['UserTestResponse ID', 'Answer ID'])
        # Write data rows
        for utr in UserTestResponse.objects.all():
            for answer in utr.correct_answers.all():
                writer.writerow([utr.id, answer.id])

# Function to export user answers data
def export_user_answers():
    with open('study_usertestresponse_user_answers.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        # Write headers
        writer.writerow(['UserTestResponse ID', 'Answer ID'])
        # Write data rows
        for utr in UserTestResponse.objects.all():
            for answer in utr.user_answers.all():
                writer.writerow([utr.id, answer.id])

# Run export functions

def import_csv_to_model(csv_filepath, model, unique_fields):
    """
    Import CSV data into the given model.

    :param csv_filepath: Path to the CSV file to import.
    :param model: Django model to which the data will be imported.
    :param unique_fields: List of fields that are used to identify duplicates.
    """
    with open(csv_filepath, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Check for identical row
            if not model.objects.filter(**row).exists():
                # Check for all fields identical except ID
                query = {field: row[field] for field in unique_fields}
                if not model.objects.filter(**query).exists():
                    try:
                        # Create a new object and save it
                        obj = model(**row)
                        obj.save()
                    except IntegrityError as e:
                        # If only IDs conflict, create a new ID then insert
                        row.pop('id', None)  # Remove conflicting ID if necessary
                        model.objects.create(**row)
                else:
                    print(f"Skipped identical row: {row}")
            else:
                print(f"Skipped duplicate row: {row}")


# Define file paths and unique fields
user_test_response_csv = './study_usertestresponse.csv'
correct_answers_csv = './study_usertestresponse_correct_answers.csv'
user_answers_csv = './study_usertestresponse_user_answers.csv'

if __name__ == "__main__":
    # Run the grouping function
    # export_user_test_responses()
    # export_correct_answers()
    # export_user_answers()
    # Import UserTestResponse
    import_csv_to_model(user_test_response_csv, UserTestResponse, ['user_id', 'question_id', 'test_date'])

    # Import Correct Answers - assuming through model exists or is auto-created by Django
    import_csv_to_model(correct_answers_csv, UserTestResponse.correct_answers.through, ['usertestresponse_id', 'answer_id'])

    # Import User Answers - assuming through model exists or is auto-created by Django
    import_csv_to_model(user_answers_csv, UserTestResponse.user_answers.through, ['usertestresponse_id', 'answer_id'])