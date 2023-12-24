import openpyxl
import random
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'picsu.settings')  # Replace 'your_project.settings' with your actual Django project's settings
django.setup()

from study.models import Word, Answer, Question

def import_data(excel_path, learning_method):
    workbook = openpyxl.load_workbook(excel_path)
    sheet = workbook.active
    all_words = []
    if learning_method == 'picsu':
        for row in sheet.iter_rows(min_row=2, values_only=True):  # Assuming first row is header
            word_text, synonym1, synonym2, synonym3, chinese_meaning, english_meaning, image_url = row

            # Create Word instance
            word, created = Word.objects.get_or_create(original_word=word_text, english_meaning=english_meaning, chinese_meaning=chinese_meaning, image_url=image_url, learning_method='picsu')

            # Create Question instance
            question = Question.objects.create(word=word)

            all_words.append(word)

            # Create Answer instances and link to Question
            for synonym in [synonym1, synonym2, synonym3]:
                if synonym:  # Skip blank synonyms
                    answer = Answer.objects.create(word=word, text=synonym)
                    question.correct_answers.add(answer)

        random.shuffle(all_words)
        halfway_point = len(all_words) // 2
        p1, p2 = all_words[:halfway_point], all_words[halfway_point:]

        for word in p1:
            Question.objects.filter(word=word).update(group='p1')
        for word in p2:
            Question.objects.filter(word=word).update(group='p2')

    elif learning_method == 'flashcard':
        for row in sheet.iter_rows(min_row=2, values_only=True):  # Assuming first row is header
            word_text, synonym1, synonym2, synonym3, chinese_meaning, english_meaning = row

            # Create Word instance
            word, created = Word.objects.get_or_create(original_word=word_text, english_meaning=english_meaning, chinese_meaning=chinese_meaning, learning_method='flashcard')

            # Create Question instance
            question = Question.objects.create(word=word)

            all_words.append(word)

            # Create Answer instances and link to Question
            for synonym in [synonym1, synonym2, synonym3]:
                if synonym:  # Skip blank synonyms
                    answer = Answer.objects.create(word=word, text=synonym)
                    question.correct_answers.add(answer)

        # Divide words into two groups
        random.shuffle(all_words)
        halfway_point = len(all_words) // 2
        f1, f2 = all_words[:halfway_point], all_words[halfway_point:]

        # Assign groups
        for word in f1:
            Question.objects.filter(word=word).update(group='f1')
        for word in f2:
            Question.objects.filter(word=word).update(group='f2')




if __name__ == "__main__":
    picsu_dict_path = 'Vocabulary_PICSU.xlsx' 
    flashcard_dict_path = 'Vocabulary_Flashcard.xlsx'
    print("Running...")
    import_data(picsu_dict_path, "picsu")
    import_data(flashcard_dict_path, "flashcard")
