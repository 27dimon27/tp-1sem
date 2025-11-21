from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Sum, Count


class LikeTypes:
    LIKE = 1
    DISLIKE = -1

    CHOICES = [
        (LIKE, "Like"),
        (DISLIKE, "Dislike"),
    ]


def validate_like_value(value):
    if value not in [LikeTypes.LIKE, LikeTypes.DISLIKE]:
        raise ValidationError(
            f"Value must be {LikeTypes.LIKE} (like) or {LikeTypes.DISLIKE} (dislike)",
            code="invalid_like_value",
        )


class ProfileManager(models.Manager):
    def best_members(self, limit=10):
        return self.annotate(total_rating=Sum("user__question__rating")).order_by(
            "-total_rating"
        )[:limit]


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name="Profile user"
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        null=True,
        blank=True,
        max_length=255,
        verbose_name="Profile avatar",
    )

    objects = ProfileManager()

    def __str__(self):
        return f"Данные профиля пользователя #{self.user_id}"


class TagManager(models.Manager):
    def popular_tags(self, limit=10):
        return self.annotate(question_count=Count("question")).order_by(
            "-question_count"
        )[:limit]


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Tag name")

    objects = TagManager()

    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def new_questions(self):
        return (
            self.select_related("author")
            .prefetch_related("tags")
            .order_by("-created_date")
        )

    def best_questions(self):
        return (
            self.select_related("author").prefetch_related("tags").order_by("-rating")
        )

    def questions_by_tag(self, tag_name):
        return (
            self.filter(tags__name=tag_name)
            .select_related("author")
            .prefetch_related("tags")
            .order_by("-created_date")
        )


class Question(models.Model):
    title = models.CharField(max_length=255, verbose_name="Question title")
    text = models.TextField(max_length=3000, verbose_name="Question text")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Question author"
    )
    tags = models.ManyToManyField(Tag, verbose_name="Question tags")
    created_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Question creation date"
    )
    rating = models.IntegerField(default=0, verbose_name="Question rating")

    objects = QuestionManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("app:question", args=[str(self.id)])

    def update_rating(self):
        data = self.question_likes.aggregate(rating=Sum("value"))
        self.rating = data["rating"] or 0
        self.save(update_fields=["rating"])


class Answer(models.Model):
    text = models.TextField(max_length=5000, verbose_name="Answer text")
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, verbose_name="Answer question"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Answer author"
    )
    created_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Answer creation date"
    )
    is_correct = models.BooleanField(default=False, verbose_name="Is answer correct")
    rating = models.IntegerField(default=0, verbose_name="Answer rating")

    def __str__(self):
        return f"Answer #{self.id} to question #{self.question_id}"

    def update_rating(self):
        data = self.answer_likes.aggregate(rating=Sum("value"))
        self.rating = data["rating"] or 0
        self.save(update_fields=["rating"])


class QuestionLike(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="User who likes the question"
    )
    question = models.ForeignKey(
        Question,
        related_name="question_likes",
        on_delete=models.CASCADE,
        verbose_name="Liked question",
    )
    value = models.SmallIntegerField(
        choices=LikeTypes.CHOICES,
        verbose_name="Like type for question",
        validators=[validate_like_value],
    )

    class Meta:
        unique_together = ["user", "question"]


class AnswerLike(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="User who likes the answer"
    )
    answer = models.ForeignKey(
        Answer,
        related_name="answer_likes",
        on_delete=models.CASCADE,
        verbose_name="Liked answer",
    )
    value = models.SmallIntegerField(
        choices=LikeTypes.CHOICES,
        verbose_name="Like type for answer",
        validators=[validate_like_value],
    )

    class Meta:
        unique_together = ["user", "answer"]
