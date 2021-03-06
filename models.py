from django.db import models
from django.contrib.auth.models import User


class Topic(models.Model):
    topic_id = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    date_added = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "<Topic: {}>".format(self.name)


class People(models.Model):
    handle = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    date_added = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "<People: {}>".format(self.name)


class Question(models.Model):
    question_id = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    date_added = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "<Question: {}>".format(self.name)


class Answer(models.Model):
    answer_id = models.CharField(max_length=20)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author_name = models.CharField(max_length=200)
    date_added = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "<Answer: {}, Question: {}>".\
            format(self.author_name, self.question.question_id)
