from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404
from .models import Question


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get("page", 1)

    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return page


def index(request):
    questions = Question.objects.new_questions()
    page = paginate(questions, request, 5)
    return render(
        request, "index.html", {"questions": page, "page_title": "New Questions"}
    )


def hot_questions(request):
    questions = Question.objects.best_questions()
    page = paginate(questions, request, 5)
    return render(
        request, "index.html", {"questions": page, "page_title": "Hot Questions"}
    )


def tag_questions(request, tag_name):
    questions = Question.objects.questions_by_tag(tag_name)
    page = paginate(questions, request, 5)
    return render(
        request,
        "index.html",
        {
            "questions": page,
            "page_title": f"Tag: {tag_name}",
            "is_tag_page": True,
            "current_tag": tag_name,
        },
    )


def question_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    answers = question.answer_set.all().order_by("-rating", "-created_date")
    page = paginate(answers, request, 5)
    return render(request, "question.html", {"question": question, "answers": page})


def login_view(request):
    return render(request, "login.html")


def signup_view(request):
    return render(request, "signup.html")


def ask_question(request):
    return render(request, "ask.html")


def settings_view(request):
    return render(request, "settings.html")
