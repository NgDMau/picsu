import openpyxl
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'picsu.settings')  # Replace 'your_project.settings' with your actual Django project's settings
django.setup()

from study.models import Word, Answer, Question

def import_data(excel_path):
    workbook = openpyxl.load_workbook(excel_path)
    sheet = workbook.active

    for row in sheet.iter_rows(min_row=2, values_only=True):  # Assuming first row is header
        word_text, synonym1, synonym2, synonym3, chinese_meaning, english_meaning, image_url = row

        # Create Word instance
        word, created = Word.objects.get_or_create(original_word=word_text, english_meaning=english_meaning, chinese_meaning=chinese_meaning, image_url=image_url)

        # Create Question instance
        question = Question.objects.create(word=word)

        # Create Answer instances and link to Question
        for synonym in [synonym1, synonym2, synonym3]:
            if synonym:  # Skip blank synonyms
                answer = Answer.objects.create(word=word, text=synonym)
                question.correct_answers.add(answer)

if __name__ == "__main__":
    path_to_excel = 'Vocabulary_PICSU.xlsx'  # Update this path
    print("Running...")
    import_data(path_to_excel)
