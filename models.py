from django.db import models


class Topic(models.Model):
    name = models.CharField(max_length=200)
    topic_id = models.CharField(max_length=20)

    def __str__(self):
        return "<Topic: {}>".format(self.name)


class People(models.Model):
    name = models.CharField(max_length=200)
    handle = models.CharField(max_length=50)

    def __str__(self):
        return "<People: {}>".format(self.name)


class Question(models.Model):
    name = models.CharField(max_length=200)
    question_id = models.CharField(max_length=20)

    def __str__(self):
        return "<Question: {}>".format(self.name)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    answer_id = models.CharField(max_length=20)

    def __str__(self):
        return "<Answer: {}, Question: {}>".\
            format(self.name, self.question.question_id)
