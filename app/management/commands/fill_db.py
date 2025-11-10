import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction, models
from app.models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("ratio", type=int, help="Ratio for data generation")

    def _create_users_and_profiles(self, ratio):
        users_to_create = []

        for i in range(ratio):
            user = User(
                username=f"user_{i}",
                email=f"user_{i}@example.com",
                password=f"password_{i}",
            )
            users_to_create.append(user)

            if len(users_to_create) >= 1000:
                User.objects.bulk_create(users_to_create)
                users_to_create = []

            if i % max(1, ratio // 100) == 0:
                self.stdout.write(f"Created {i} users...")

        if users_to_create:
            User.objects.bulk_create(users_to_create)

        users = list(User.objects.all())
        profiles_to_create = [Profile(user=user) for user in users]
        Profile.objects.bulk_create(profiles_to_create)

        return users

    def _create_tags(self, ratio):
        tags_to_create = []

        for i in range(ratio):
            tags_to_create.append(Tag(name=f"tag_{i}"))

            if len(tags_to_create) >= 1000:
                Tag.objects.bulk_create(tags_to_create)
                tags_to_create = []

            if i % max(1, ratio // 100) == 0:
                self.stdout.write(f"Created {i} tags...")

        if tags_to_create:
            Tag.objects.bulk_create(tags_to_create)

        return list(Tag.objects.all())

    def _create_questions(self, ratio, users, tags):
        questions_to_create = []

        for i in range(ratio * 10):
            author = random.choice(users)
            question = Question(
                title=f"Question title {i}",
                text=f"This is the text of question {i}. " * 3,
                author=author,
                rating=0,
            )
            questions_to_create.append(question)

            if len(questions_to_create) >= 1000:
                Question.objects.bulk_create(questions_to_create)
                questions_to_create = []

            if i % max(1, (ratio * 10) // 100) == 0:
                self.stdout.write(f"Created {i} questions...")

        if questions_to_create:
            Question.objects.bulk_create(questions_to_create)

        questions = list(Question.objects.all())

        self.stdout.write("Adding tags to questions...")
        question_tags = []
        for question in questions:
            question_tags_list = random.sample(tags, min(3, len(tags)))
            for tag in question_tags_list:
                question_tags.append(
                    Question.tags.through(question_id=question.id, tag_id=tag.id)
                )

            if len(question_tags) >= 10000:
                Question.tags.through.objects.bulk_create(question_tags)
                question_tags = []

        if question_tags:
            Question.tags.through.objects.bulk_create(question_tags)

        return questions

    def _create_answers(self, ratio, users, questions):
        answers_to_create = []

        for i in range(ratio * 100):
            question = random.choice(questions)
            author = random.choice(users)
            answer = Answer(
                text=f"This is answer {i} to question. " * 3,
                question=question,
                author=author,
                rating=0,
                is_correct=random.choice([True, False]),
            )
            answers_to_create.append(answer)

            if len(answers_to_create) >= 5000:
                Answer.objects.bulk_create(answers_to_create)
                answers_to_create = []

            if i % max(1, (ratio * 100) // 100) == 0:
                self.stdout.write(f"Created {i} answers...")

        if answers_to_create:
            Answer.objects.bulk_create(answers_to_create)

        return list(Answer.objects.all())

    def _create_question_likes(self, ratio, users, questions):
        total_likes = ratio * 200
        target_count = total_likes // 4
        likes_to_create = []
        created_count = 0

        rating_changes = {}

        existing_likes = set(QuestionLike.objects.values_list("user_id", "question_id"))

        valid_pairs = []
        for _ in range(target_count * 3):
            user = random.choice(users)
            question = random.choice(questions)
            if user.id != question.author_id:
                valid_pairs.append((user.id, question.id))

        valid_pairs = list(set(valid_pairs))
        random.shuffle(valid_pairs)

        for user_id, question_id in valid_pairs:
            if created_count >= target_count:
                break

            if (user_id, question_id) not in existing_likes:
                value = random.choice([1, -1])
                likes_to_create.append(
                    QuestionLike(user_id=user_id, question_id=question_id, value=value)
                )

                if question_id not in rating_changes:
                    rating_changes[question_id] = 0
                rating_changes[question_id] += value

                existing_likes.add((user_id, question_id))
                created_count += 1

                if len(likes_to_create) >= 1000:
                    QuestionLike.objects.bulk_create(likes_to_create)
                    likes_to_create = []

                    self._update_ratings_batch(Question, rating_changes)
                    rating_changes = {}

                if created_count % max(1, target_count // 100) == 0:
                    self.stdout.write(
                        f"Created {created_count}/{target_count} question likes..."
                    )

        if likes_to_create:
            QuestionLike.objects.bulk_create(likes_to_create)

        if rating_changes:
            self._update_ratings_batch(Question, rating_changes)

        self._refresh_question_ratings(questions)

        return created_count

    def _create_answer_likes(self, ratio, users, answers):
        total_likes = ratio * 200
        target_count = total_likes - (total_likes // 4)
        likes_to_create = []
        created_count = 0

        rating_changes = {}

        existing_likes = set(AnswerLike.objects.values_list("user_id", "answer_id"))

        valid_pairs = []
        for _ in range(target_count * 3):
            user = random.choice(users)
            answer = random.choice(answers)
            if user.id != answer.author_id:
                valid_pairs.append((user.id, answer.id))

        valid_pairs = list(set(valid_pairs))
        random.shuffle(valid_pairs)

        for user_id, answer_id in valid_pairs:
            if created_count >= target_count:
                break

            if (user_id, answer_id) not in existing_likes:
                value = random.choice([1, -1])
                likes_to_create.append(
                    AnswerLike(user_id=user_id, answer_id=answer_id, value=value)
                )

                if answer_id not in rating_changes:
                    rating_changes[answer_id] = 0
                rating_changes[answer_id] += value

                existing_likes.add((user_id, answer_id))
                created_count += 1

                if len(likes_to_create) >= 1000:
                    AnswerLike.objects.bulk_create(likes_to_create)
                    likes_to_create = []

                    self._update_ratings_batch(Answer, rating_changes)
                    rating_changes = {}

                if created_count % max(1, target_count // 100) == 0:
                    self.stdout.write(
                        f"Created {created_count}/{target_count} answer likes..."
                    )

        if likes_to_create:
            AnswerLike.objects.bulk_create(likes_to_create)

        if rating_changes:
            self._update_ratings_batch(Answer, rating_changes)

        self._refresh_answer_ratings(answers)

        return created_count

    def _update_ratings_batch(self, model, rating_changes):
        from django.db import connection

        table_name = "app_question" if model == Question else "app_answer"

        with connection.cursor() as cursor:
            for obj_id, rating_change in rating_changes.items():
                cursor.execute(
                    f"UPDATE {table_name} SET rating = rating + %s WHERE id = %s",
                    [rating_change, obj_id],
                )

    def _refresh_question_ratings(self, questions):
        self.stdout.write("Refreshing question ratings in memory...")
        question_ids = [q.id for q in questions]
        refreshed_questions = Question.objects.in_bulk(question_ids)

        for question in questions:
            if question.id in refreshed_questions:
                question.rating = refreshed_questions[question.id].rating

    def _refresh_answer_ratings(self, answers):
        self.stdout.write("Refreshing answer ratings in memory...")
        answer_ids = [a.id for a in answers]
        refreshed_answers = Answer.objects.in_bulk(answer_ids)

        for answer in answers:
            if answer.id in refreshed_answers:
                answer.rating = refreshed_answers[answer.id].rating

    def _verify_ratings(self, questions, answers):
        self.stdout.write("Verifying rating consistency...")

        question_mismatches = 0
        for question in questions[:20]:
            real_rating = (
                QuestionLike.objects.filter(question=question).aggregate(
                    total=models.Sum("value")
                )["total"]
                or 0
            )
            if question.rating != real_rating:
                question_mismatches += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"Question {question.id}: DB rating={question.rating}, "
                        f"Real rating={real_rating}"
                    )
                )

        answer_mismatches = 0
        for answer in answers[:20]:
            real_rating = (
                AnswerLike.objects.filter(answer=answer).aggregate(
                    total=models.Sum("value")
                )["total"]
                or 0
            )
            if answer.rating != real_rating:
                answer_mismatches += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"Answer {answer.id}: DB rating={answer.rating}, "
                        f"Real rating={real_rating}"
                    )
                )

        if question_mismatches == 0 and answer_mismatches == 0:
            self.stdout.write(self.style.SUCCESS("✓ All ratings are consistent!"))
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Found {question_mismatches} question and {answer_mismatches} answer rating mismatches"
                )
            )

    @transaction.atomic
    def handle(self, *args, **options):
        ratio = options["ratio"]
        total_target_likes = ratio * 200
        question_target = total_target_likes // 4
        answer_target = total_target_likes - question_target

        self.stdout.write("Clearing existing data...")
        QuestionLike.objects.all().delete()
        AnswerLike.objects.all().delete()
        Answer.objects.all().delete()
        Question.objects.all().delete()
        Tag.objects.all().delete()
        Profile.objects.all().delete()
        User.objects.all().delete()

        self.stdout.write("Creating users and profiles...")
        users = self._create_users_and_profiles(ratio)

        self.stdout.write("Creating tags...")
        tags = self._create_tags(ratio)

        self.stdout.write("Creating questions...")
        questions = self._create_questions(ratio, users, tags)

        self.stdout.write("Creating answers...")
        answers = self._create_answers(ratio, users, questions)

        self.stdout.write(f"Creating question likes ({question_target} target)...")
        question_likes_count = self._create_question_likes(ratio, users, questions)

        self.stdout.write(f"Creating answer likes ({answer_target} target)...")
        answer_likes_count = self._create_answer_likes(ratio, users, answers)

        self._verify_ratings(questions, answers)

        total_created_likes = question_likes_count + answer_likes_count

        self.stdout.write("\nSample question ratings:")
        for question in questions[:5]:
            self.stdout.write(f"  Question {question.id}: rating = {question.rating}")

        self.stdout.write("\nSample answer ratings:")
        for answer in answers[:5]:
            self.stdout.write(f"  Answer {answer.id}: rating = {answer.rating}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully filled database:\n"
                f"- Users: {len(users)}\n"
                f"- Tags: {len(tags)}\n"
                f"- Questions: {len(questions)}\n"
                f"- Answers: {len(answers)}\n"
                f"- Question likes: {question_likes_count}\n"
                f"- Answer likes: {answer_likes_count}\n"
                f"- Total likes: {total_created_likes}"
            )
        )
