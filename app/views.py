from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import FormView
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpRequest
from django.db import transaction
from .models import Question, Tag, Profile
from .forms import LoginForm, SignupForm, AskForm, AnswerForm, SettingsForm, ProfileForm

ITEMS_PER_PAGE = 5


def get_common_context():
    popular_tags = Tag.objects.popular_tags(8)
    best_members = Profile.objects.best_members(4)

    return {
        "popular_tags": popular_tags,
        "best_members": best_members,
    }


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


def index(request: HttpRequest):
    questions = Question.objects.new_questions()
    page = paginate(questions, request, ITEMS_PER_PAGE)
    context = {"questions": page, "page_title": "New Questions"}
    context.update(get_common_context())
    return render(request, "index.html", context)


def hot_questions(request: HttpRequest):
    questions = Question.objects.best_questions()
    page = paginate(questions, request, ITEMS_PER_PAGE)
    context = {"questions": page, "page_title": "Hot Questions"}
    context.update(get_common_context())
    return render(request, "index.html", context)


def tag_questions(request: HttpRequest, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    questions = (
        Question.objects.questions_by_tag(tag)
        .select_related("author")
        .prefetch_related("tags", "author__profile", "answer_set")
        .order_by("-created_date")
    )
    page = paginate(questions, request, ITEMS_PER_PAGE)
    context = {
        "questions": page,
        "page_title": f"Tag: {tag_name}",
        "is_tag_page": True,
        "current_tag": tag_name,
    }
    context.update(get_common_context())
    return render(request, "index.html", context)


@login_required(login_url="app:login")
def create_answer(request: HttpRequest, question_id):
    question = get_object_or_404(Question, id=question_id)

    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.author = request.user
            answer.save()

            return redirect(f"{question.get_absolute_url()}#answer-{answer.id}")

    return redirect(question.get_absolute_url())


def question_detail(request: HttpRequest, question_id):
    question = get_object_or_404(
        Question.objects.select_related("author").prefetch_related("tags"),
        id=question_id,
    )
    answers = (
        question.answer_set.all()
        .select_related("author")
        .select_related("author__profile")
        .order_by("-rating", "-created_date")
    )
    page = paginate(answers, request, ITEMS_PER_PAGE)
    form = AnswerForm()

    context = {"question": question, "answers": page, "form": form}
    context.update(get_common_context())
    return render(request, "question.html", context)


def login_view(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect("app:settings")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get("next", "app:index")
                return redirect(next_url)
    else:
        form = LoginForm()

    context = {"form": form}
    context.update(get_common_context())
    return render(request, "login.html", context)


def logout_view(request: HttpRequest):
    current_path: str = request.META.get("HTTP_REFERER")
    logout(request)
    protected_paths = [
        "/settings/",
        "/ask/",
    ]

    redirect_to_index = any(current_path.endswith(path) for path in protected_paths)
    if redirect_to_index:
        return redirect("app:index")
    return redirect(request.META.get("HTTP_REFERER", "app:index"))


def signup_view(request: HttpRequest):
    if request.method == "POST":
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("app:index")
    else:
        form = SignupForm()

    context = {"form": form}
    context.update(get_common_context())
    return render(request, "signup.html", context)


@login_required(login_url="app:login")
def ask_question(request: HttpRequest):
    if request.method == "POST":
        form = AskForm(request.POST)
        if form.is_valid():
            question = form.save(author=request.user)
            return redirect(question.get_absolute_url())
    else:
        form = AskForm()

    context = {"form": form}
    context.update(get_common_context())
    return render(request, "ask.html", context)


class SettingsView(LoginRequiredMixin, FormView):
    template_name = "settings.html"
    form_class = SettingsForm
    success_url = reverse_lazy("app:settings")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_common_context())
        user_profile, _ = Profile.objects.get_or_create(user=self.request.user)
        if self.request.method == "POST":
            context["profile_form"] = ProfileForm(
                self.request.POST,
                self.request.FILES,
                instance=user_profile,
            )
        else:
            context["profile_form"] = ProfileForm(instance=user_profile)
        return context

    @transaction.atomic
    def form_valid(self, form):
        user = form.save(commit=False)
        user_profile, _ = Profile.objects.get_or_create(user=user)
        profile_form = ProfileForm(
            self.request.POST, self.request.FILES, instance=user_profile
        )
        if profile_form.is_valid():
            user.save()
            profile_form.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


def settings_view(request: HttpRequest):
    view = SettingsView.as_view()
    return view(request)
