from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Question, Tag, Profile
from .forms import SettingsForm, ProfileForm
from django.core.cache import cache


def get_common_context():
    popular_tags = cache.get("popular_tags")
    if popular_tags is None:
        popular_tags = Tag.objects.popular_tags(8)
        cache.set("popular_tags", popular_tags, 300)

    best_members = cache.get("best_members")
    if best_members is None:
        best_members = Profile.objects.best_members(4)
        cache.set("best_members", best_members, 300)

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


def index(request):
    questions = (
        Question.objects.new_questions()
        .select_related("author")
        .prefetch_related("tags")
    )
    page = paginate(questions, request, 5)
    context = {"questions": page, "page_title": "New Questions"}
    context.update(get_common_context())
    return render(request, "index.html", context)


def hot_questions(request):
    questions = (
        Question.objects.best_questions()
        .select_related("author")
        .prefetch_related("tags")
    )
    page = paginate(questions, request, 5)
    context = {"questions": page, "page_title": "Hot Questions"}
    context.update(get_common_context())
    return render(request, "index.html", context)


def tag_questions(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    questions = (
        Question.objects.questions_by_tag(tag)
        .select_related("author")
        .prefetch_related("tags")
        .order_by("-created_date")
    )
    page = paginate(questions, request, 5)
    context = {
        "questions": page,
        "page_title": f"Tag: {tag_name}",
        "is_tag_page": True,
        "current_tag": tag_name,
    }
    context.update(get_common_context())
    return render(request, "index.html", context)


def question_detail(request, question_id):
    question = get_object_or_404(
        Question.objects.select_related("author").prefetch_related("tags"),
        id=question_id,
    )
    answers = (
        question.answer_set.all()
        .select_related("author")
        .order_by("-rating", "-created_date")
    )
    page = paginate(answers, request, 5)
    context = {"question": question, "answers": page}
    context.update(get_common_context())
    return render(request, "question.html", context)


def login_view(request):
    context = get_common_context()
    return render(request, "login.html", context)


def signup_view(request):
    context = get_common_context()
    return render(request, "signup.html", context)


def ask_question(request):
    context = get_common_context()
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
        if self.request.method == "POST":
            context["profile_form"] = ProfileForm(
                self.request.POST,
                self.request.FILES,
                instance=self.request.user.profile,
            )
        else:
            context["profile_form"] = ProfileForm(instance=self.request.user.profile)
        return context

    def form_valid(self, form):
        form.save()
        profile_form = ProfileForm(
            self.request.POST, self.request.FILES, instance=self.request.user.profile
        )
        if profile_form.is_valid():
            profile_form.save()
        return super().form_valid(form)


def settings_view(request):
    view = SettingsView.as_view()
    return view(request)
