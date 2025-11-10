from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    def __str__(self):
        return self.user.username


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def new_questions(self):
        return self.order_by("-created_date")

    def best_questions(self):
        return self.order_by("-rating")

    def questions_by_tag(self, tag_name):
        return self.filter(tags__name=tag_name).order_by("-created_date")


class Question(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    created_date = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    objects = QuestionManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("app:question", args=[str(self.id)])

    def update_rating(self):
        question_likes = QuestionLike.objects.filter(question=self)
        self.rating = sum(like.value for like in question_likes)
        self.save()


class Answer(models.Model):
    text = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(default=False)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f"Answer to {self.question.title}"

    def update_rating(self):
        answer_likes = AnswerLike.objects.filter(answer=self)
        self.rating = sum(like.value for like in answer_likes)
        self.save()


class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=[(1, "Like"), (-1, "Dislike")])

    class Meta:
        unique_together = ["user", "question"]

    def save(self, *args, **kwargs):
        if self.value not in [1, -1]:
            raise ValidationError("Value must be 1 (like) or -1 (dislike)")
        super().save(*args, **kwargs)


class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=[(1, "Like"), (-1, "Dislike")])

    class Meta:
        unique_together = ["user", "answer"]

    def save(self, *args, **kwargs):
        if self.value not in [1, -1]:
            raise ValidationError("Value must be 1 (like) or -1 (dislike)")
        super().save(*args, **kwargs)
