from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class LikeTypes:
    LIKE = 1
    DISLIKE = -1

    CHOICES = [
        (LIKE, "Like"),
        (DISLIKE, "Dislike"),
    ]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Profile user")
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True, max_length=255, verbose_name="Profile avatar")

    def __str__(self):
        return f"Данные профиля пользователя #{self.user_id}"


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Tag name")

    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def new_questions(self):
        return self.order_by("-created_date")

    def best_questions(self):
        return self.order_by("-rating")

    def questions_by_tag(self, tag):
        return self.filter(tags=tag).order_by("-created_date")


class Question(models.Model):
    title = models.CharField(max_length=255, verbose_name="Question title")
    text = models.TextField(max_length=3000, verbose_name="Question text")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Question author")
    tags = models.ManyToManyField(Tag, verbose_name="Question tags")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Question creation date")
    rating = models.IntegerField(default=0, verbose_name="Question rating")

    objects = QuestionManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("app:question", args=[str(self.id)])

    def update_rating(self):
        question_likes = QuestionLike.objects.filter(question=self)
        self.rating = sum(like.value for like in question_likes)
        self.save(update_fields=["rating"])


class Answer(models.Model):
    text = models.TextField(max_length=5000, verbose_name="Answer text")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="Answer question")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Answer author")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Answer creation date")
    is_correct = models.BooleanField(default=False, verbose_name="Is answer correct")
    rating = models.IntegerField(default=0, verbose_name="Answer rating")

    def __str__(self):
        return f"Answer #{self.id} to question #{self.question_id}"

    def update_rating(self):
        answer_likes = AnswerLike.objects.filter(answer=self)
        self.rating = sum(like.value for like in answer_likes)
        self.save(update_fields=["rating"])


class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User who likes the question")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="Liked question")
    value = models.SmallIntegerField(choices=LikeTypes.CHOICES, verbose_name="Like type for question")

    class Meta:
        unique_together = ["user", "question"]
    
    def clean(self):
        if self.value not in [LikeTypes.LIKE, LikeTypes.DISLIKE]:
            raise ValidationError("Value must be 1 (like) or -1 (dislike)")
        
        if self.user == self.question.author:
            raise ValidationError("You cannot like your own question")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User who likes the answer")
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, verbose_name="Liked answer")
    value = models.SmallIntegerField(choices=LikeTypes.CHOICES, verbose_name="Like type for answer")

    class Meta:
        unique_together = ["user", "answer"]
    
    def clean(self):
        if self.value not in [LikeTypes.LIKE, LikeTypes.DISLIKE]:
            raise ValidationError("Value must be 1 (like) or -1 (dislike)")
        
        if self.user == self.answer.author:
            raise ValidationError("You cannot like your own answer")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
