from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.core.serializers import serialize
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q
import json
import random
from .models import Question, Word, Answer, UserLearnedWord, UserTestResponse, UserTestScore
from user.models import UserProfile, UserKnownAnswer, UserUnknownWord


def index(request):
    return render(request, "study/index.html")

@login_required
def home(request):
    user = request.user
    userinfo = UserProfile.objects.get(user=user)
    context = {"user_info": {
        'id': user.id,
        'username': user.username,
        "picsu_dict": userinfo.picsu_dict,
        "flashcard_dict": userinfo.flashcard_dict
    }}
    return render(request, "study/home.html", context)


def create_test_for_user(user, learning_method):
    user_profile = UserProfile.objects.get(user=user)
    user_picsu_dict = user_profile.picsu_dict
    user_flashcard_dict = user_profile.flashcard_dict
    # Step 1: Get questions with words the user has learned
    learned_words_ids = UserLearnedWord.objects.filter(user=user).values_list('word', flat=True)
    if learning_method == "picsu":
        questions_with_learned_words = Question.objects.filter(group=user_picsu_dict, word__id__in=learned_words_ids, word__learning_method=learning_method)
    elif learning_method == "flashcard":
        questions_with_learned_words = Question.objects.filter(group=user_flashcard_dict, word__id__in=learned_words_ids, word__learning_method=learning_method)
    else:
        print("WRONG LEARNING METHOD")
        return

    test_questions = []

    # Step 2: For each question, add 5 random answers from other questions
    for question in questions_with_learned_words:
        print("Question id: ", question.id)
        correct_answers = list(question.correct_answers.all())
        random_answers = list(Answer.objects.exclude(question=question).order_by('?')[:5])
        all_answers = correct_answers + random_answers

        # Step 3: Shuffle the combined answers
        random.shuffle(all_answers)

        test_questions.append({
            'question': question,
            'answers': all_answers
        })
    
    

    return test_questions


def calculate_and_store_user_score(user, type):
    responses = UserTestResponse.objects.filter(user=user)
    total_chosen = sum(response.user_answers.count() for response in responses)
    correct_count = sum(answer in response.correct_answers.all() for response in responses for answer in response.user_answers.all())
    incorrect_count = total_chosen - correct_count

    # Store the results
    test_score = UserTestScore.objects.create(
        user=user,
        type=type,
        total_answers_chosen=total_chosen,
        correct_answers_count=correct_count,
        incorrect_answers_count=incorrect_count
    )
    return test_score

@login_required
def result(request, test_score_id):
    test_score = UserTestScore.objects.get(id=test_score_id, user=request.user)
    return render(request, 'study/results.html', {'test_score': test_score})






@login_required
def pretest(request):
    # CREATE A SET OF VOCABULARY FOR USER TO LEARN
    if request.method == "GET":
        user = request.user

        if not UserProfile.objects.filter(user=user).exists():
            user_profile=UserProfile.objects.create(user=user)
        
        user_profile = UserProfile.objects.get(user=user)
        user_picsu_dict = user_profile.picsu_dict
        user_flashcard_dict = user_profile.flashcard_dict

        print("USER DICT NOTE: ", user_picsu_dict, user_flashcard_dict)

        unknown_words_ids = UserUnknownWord.objects.filter(user=user_profile).values_list('word', flat=True)
        # Querying all words that are not in the unknown words
        print("Unknown words ids: ", unknown_words_ids)
        words = Word.objects.filter(
            Q(question__group=user_picsu_dict) or Q(question__group=user_flashcard_dict)
        ).exclude(id__in=unknown_words_ids)

        print("WORDS LEN: ", len(words))

        words_data = []
        for word in words:
            word_dict = {
                'word': word.original_word,  # Assuming 'original_word' is a field in 'Word' model
                'id': word.id
            }
            words_data.append(word_dict)

        words_json = json.dumps(words_data)

        return render(request, "study/pretest.html", {'words': words_json})

    elif request.method == 'POST':
        data = json.loads(request.body)
        word_id = data.get('word_id')
        word = Word.objects.get(id=word_id)
        user = request.user

        if not UserProfile.objects.filter(user=user).exists():
            UserProfile.objects.create(user=user)

        user_profile = UserProfile.objects.get(user=user)

        if not UserUnknownWord.objects.filter(user=user_profile, word=word).exists():
            UserUnknownWord.objects.create(user=user_profile, word=word)
            print("Inserted unknown word")
        
        # print("{} does not know {} {}".format(user.username, word_id, word))
        return HttpResponse(status=200)


@login_required
def learning_picsu(request):
    if request.method == "GET":
        # Load 50 questions containing Words and Answers
        # filter so that user:
        #                     - Knows the words
        #                     - Has not known the synonym 

        # List all words id that User does not know
        user = request.user
        user_profile=UserProfile.objects.get(user=user)
        user_picsu_dict = user_profile.picsu_dict
        user_flashcard_dict = user_profile.flashcard_dict

        unknown_words = UserUnknownWord.objects.filter(user=user_profile).values_list('word', flat=True)

        # List all answers id that User already knows
        known_answers = UserKnownAnswer.objects.filter(user=user_profile).values_list('answer', flat=True)
        # print("Known answer: ", known_answers)

        questions = Question.objects.filter(
            Q(group=user_picsu_dict)
        ).exclude(word__original_word__in=unknown_words)
        
        # questions = Question.objects.all()[:10]
        questions_data = []
        for question in questions:
            if not UserLearnedWord.objects.filter(user=user, word=question.word).exists():
                UserLearnedWord.objects.create(user=user, word=question.word)
            unknown_answers = question.correct_answers.exclude(id__in=known_answers)
            # print("Unknown answer: ", unknown_answers)
            question_dict = {
                'image_url': question.word.image_url,
                'chinese_meaning': question.word.chinese_meaning,
                'english_meaning': question.word.english_meaning,
                'word': question.word.original_word,  # Assuming 'original_word' is a field in 'Word' model
                'answers': [{'id': answer.id ,'text': answer.text} for answer in unknown_answers]  # Assuming 'text' is a field in 'Answer' model
            }
            questions_data.append(question_dict)

        questions_json = json.dumps(questions_data)

        return render(request, "study/picsu_learning.html", {'questions': questions_json})

    elif request.method == 'POST':
        data = json.loads(request.body)
        synonym_id = data.get('synonym_id')
        answer = Answer.objects.get(id=synonym_id)
        user = request.user

        if not UserProfile.objects.filter(user=user).exists():
            UserProfile.objects.create(user=user)

        user_profile = UserProfile.objects.get(user=user)

        if not UserKnownAnswer.objects.filter(user=user_profile, answer=answer).exists():
            UserKnownAnswer.objects.create(user=user_profile, answer=answer)
        
        print("{} already knows {}".format(user.username, synonym_id))
        return HttpResponse(status=200)
    


@login_required
def first_test_picsu(request):
    user = request.user
    if request.method == "GET":
        
        test_questions = create_test_for_user(user, 'picsu')
        for question in test_questions:
            print("Test questions word: ", question["question"].id)
        print("LENGTH: ", len(test_questions))
        return render(request, 'study/picsu_first_test.html', {'test_questions': test_questions})
    
    elif request.method == 'POST':
        for key, value_list in request.POST.lists():
            if key.startswith('question_'):
                question_id = key.split('_')[1]
                question = Question.objects.get(id=question_id)
                # print("Question: ", question)
                # Get correct answers for the question
                correct_answers = question.correct_answers.all()

                # Get user selected answers
                user_answers_ids = [int(id) for id in value_list]
                user_answers = Answer.objects.filter(id__in=user_answers_ids)
                # print("User answers: ", user_answers)
                # Create UserTestResponse
                response = UserTestResponse.objects.create(user=user, question=question)
                response.correct_answers.set(correct_answers)
                response.user_answers.set(user_answers)
                response.save()

        # Redirect to a result page or another desired page
        test_score = calculate_and_store_user_score(request.user, type="first_test_picsu")

    # Redirect to the test results page or another page as desired
        return redirect('result', test_score_id=test_score.id)



@login_required
def learning_flashcard(request):
    if request.method == "GET":
        # Load 50 questions containing Words and Answers
        # filter so that user:
        #                     - Knows the words
        #                     - Has not known the synonym 

        # List all words id that User does not know
        user = request.user
        user_profile=UserProfile.objects.get(user=user)
        user_flashcard_dict = user_profile.flashcard_dict

        unknown_words = UserUnknownWord.objects.filter(user=user_profile).values_list('word', flat=True)

        # List all answers id that User already knows
        known_answers = UserKnownAnswer.objects.filter(user=user_profile).values_list('answer', flat=True)
        # print("Known answer: ", known_answers)

        questions = Question.objects.filter(
           Q(group=user_flashcard_dict)
        ).exclude(word__original_word__in=unknown_words)
        
        # questions = Question.objects.all()[:10]
        questions_data = []
        for question in questions:
            if not UserLearnedWord.objects.filter(user=user, word=question.word).exists():
                UserLearnedWord.objects.create(user=user, word=question.word)
            unknown_answers = question.correct_answers.exclude(id__in=known_answers)
            # print("Unknown answer: ", unknown_answers)
            question_dict = {
                # 'image_url': question.word.image_url,
                'chinese_meaning': question.word.chinese_meaning,
                'english_meaning': question.word.english_meaning,
                'word': question.word.original_word,  # Assuming 'original_word' is a field in 'Word' model
                'answers': [{'id': answer.id ,'text': answer.text} for answer in unknown_answers]  # Assuming 'text' is a field in 'Answer' model
            }
            questions_data.append(question_dict)

        questions_json = json.dumps(questions_data)

        return render(request, "study/flashcard_learning.html", {'questions': questions_json})

    elif request.method == 'POST':
        data = json.loads(request.body)
        synonym_id = data.get('synonym_id')
        answer = Answer.objects.get(id=synonym_id)
        user = request.user

        if not UserProfile.objects.filter(user=user).exists():
            UserProfile.objects.create(user=user)

        user_profile = UserProfile.objects.get(user=user)

        if not UserKnownAnswer.objects.filter(user=user_profile, answer=answer).exists():
            UserKnownAnswer.objects.create(user=user_profile, answer=answer)
        
        print("{} already knows {}".format(user.username, synonym_id))
        return HttpResponse(status=200)



@login_required
def first_test_flashcard(request):
    user = request.user
    if request.method == "GET":
        
        test_questions = create_test_for_user(user, learning_method="flashcard")
        # print("Test questions: ", test_questions)
        return render(request, 'study/flashcard_first_test.html', {'test_questions': test_questions})
    elif request.method == 'POST':
        for key, value_list in request.POST.lists():
            if key.startswith('question_'):
                question_id = key.split('_')[1]
                question = Question.objects.get(id=question_id)
                # print("Question: ", question)
                # Get correct answers for the question
                correct_answers = question.correct_answers.all()

                # Get user selected answers
                user_answers_ids = [int(id) for id in value_list]
                user_answers = Answer.objects.filter(id__in=user_answers_ids)
                # print("User answers: ", user_answers)
                # Create UserTestResponse
                response = UserTestResponse.objects.create(user=user, question=question)
                response.correct_answers.set(correct_answers)
                response.user_answers.set(user_answers)
                response.save()

        # Redirect to a result page or another desired page
        test_score = calculate_and_store_user_score(request.user, type="first_test_flashcard")

    # Redirect to the test results page or another page as desired
        return redirect('result', test_score_id=test_score.id)



@login_required
def retention_test_picsu(request):
    user = request.user
    if request.method == "GET":
        
        test_questions = create_test_for_user(user, learning_method="picsu")
        # print("Test questions: ", test_questions)
        return render(request, 'study/picsu_retention_test.html', {'test_questions': test_questions})
    elif request.method == 'POST':
        for key, value_list in request.POST.lists():
            if key.startswith('question_'):
                question_id = key.split('_')[1]
                question = Question.objects.get(id=question_id)
                # print("Question: ", question)
                # Get correct answers for the question
                correct_answers = question.correct_answers.all()

                # Get user selected answers
                user_answers_ids = [int(id) for id in value_list]
                user_answers = Answer.objects.filter(id__in=user_answers_ids)
                # print("User answers: ", user_answers)
                # Create UserTestResponse
                response = UserTestResponse.objects.create(user=user, question=question)
                response.correct_answers.set(correct_answers)
                response.user_answers.set(user_answers)
                response.save()

        # Redirect to a result page or another desired page
        test_score = calculate_and_store_user_score(request.user, type="retention_test_picsu")

    # Redirect to the test results page or another page as desired
        return redirect('result', test_score_id=test_score.id)




@login_required
def retention_test_flashcard(request):
    user = request.user
    if request.method == "GET":
        
        test_questions = create_test_for_user(user, learning_method="flashcard")
        # print("Test questions: ", test_questions)
        return render(request, 'study/flashcard_retention_test.html', {'test_questions': test_questions})
    elif request.method == 'POST':
        for key, value_list in request.POST.lists():
            if key.startswith('question_'):
                question_id = key.split('_')[1]
                question = Question.objects.get(id=question_id)
                # print("Question: ", question)
                # Get correct answers for the question
                correct_answers = question.correct_answers.all()

                # Get user selected answers
                user_answers_ids = [int(id) for id in value_list]
                user_answers = Answer.objects.filter(id__in=user_answers_ids)
                # print("User answers: ", user_answers)
                # Create UserTestResponse
                response = UserTestResponse.objects.create(user=user, question=question)
                response.correct_answers.set(correct_answers)
                response.user_answers.set(user_answers)
                response.save()

        # Redirect to a result page or another desired page
        test_score = calculate_and_store_user_score(request.user, type="retention_test_flashcard")

    # Redirect to the test results page or another page as desired
        return redirect('result', test_score_id=test_score.id)





@login_required
def dashboard(request):
    if request.method == "GET":

        # Get all user information
        test_scores = UserTestScore.objects.all().select_related('user')

         

        return render(request, "study/dashboard.html", {'test_scores': test_scores})




