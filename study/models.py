from django.db import models
from django.contrib.auth.models import User


class Word(models.Model):
    original_word = models.CharField(max_length=100)
    english_meaning = models.CharField(max_length=100)
    chinese_meaning = models.CharField(max_length=100)
    image_url = models.CharField(max_length=512, null=True, blank=True)
    learning_method = models.CharField(max_length=32, null=True)

    def __str__(self):
        return self.original_word
    

class Answer(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    text = models.CharField(max_length=100)  # The text of the answer

    def __str__(self):
        return self.text


class Question(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    correct_answers = models.ManyToManyField(Answer)
    group = models.CharField(max_length=32, null=True)

    def __str__(self):
        return f"Question for {self.word.original_word}"
    

class UserLearnedWord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    learned_date = models.DateField(auto_now_add=True)
    # You can add more fields like proficiency level, times reviewed, etc.

    class Meta:
        unique_together = ('user', 'word')  # To ensure unique combination for each user-word pair


class UserTest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=32, null=True)
    date_taken = models.DateTimeField(auto_now_add=True)


class UserAnswer(models.Model):
    user_test = models.ForeignKey(UserTest, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user_answer = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)


class UserTestResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    correct_answers = models.ManyToManyField(Answer, related_name='correct_for')
    user_answers = models.ManyToManyField(Answer, related_name='chosen_by_user')
    test_date = models.DateTimeField(auto_now_add=True)


class UserTestScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_answers_chosen = models.IntegerField(default=0)
    correct_answers_count = models.IntegerField(default=0)
    incorrect_answers_count = models.IntegerField(default=0)
    test_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Test on {self.test_date}"