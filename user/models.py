from django.db import models
from django.contrib.auth.models import User
from study.models import Word, Answer


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    unknown_words = models.ManyToManyField(Word, through='UserUnknownWord')

    def __str__(self):
        return self.user.username
    

class UserUnknownWord(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'word')

    def __str__(self):
        return f"{self.user.username} knows {self.word.japanese_word}"


class UserKnownAnswer(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    known_since = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'answer')

