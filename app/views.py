from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render

def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)
    
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    
    return page

def index(request):
    questions = []
    for i in range(1, 31):
        questions.append({
            'title': f'How to build a moon park? {i}',
            'id': i,
            'text': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Facere sunt reiciendis iure dolor ex, cumque laborum quibusdam repudiandae distinctio ipsum rem aut.',
            'answers_count': i % 10,
            'rating': 5 - (i % 3),
            'tags': ['black-jack', 'bender'],
        })
    
    page = paginate(questions, request, 5)
    return render(request, 'index.html', {'questions': page, 'page_title': 'New Questions'})

def hot_questions(request):
    questions = []
    for i in range(1, 18):
        questions.append({
            'title': f'Hot Question {i}',
            'id': i,
            'text': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Facere sunt reiciendis iure dolor ex, cumque laborum quibusdam repudiandae distinctio ipsum rem aut.',
            'answers_count': 10 + i,
            'rating': 15 + i,
            'tags': ['black-jack', 'bender'],
        })
    
    page = paginate(questions, request, 5)
    return render(request, 'index.html', {'questions': page, 'page_title': 'Hot Questions'})

def tag_questions(request, tag_name):
    questions = []
    for i in range(1, 20):
        questions.append({
            'title': f'Question about {tag_name} {i}',
            'id': i,
            'text': f'This question is related to {tag_name} tag.',
            'answers_count': i % 8,
            'rating': 3 + (i % 4),
            'tags': [tag_name],
        })
    
    page = paginate(questions, request, 5)
    return render(request, 'index.html', {
        'questions': page, 
        'page_title': f'Tag: {tag_name}',
        'is_tag_page': True,
        'current_tag': tag_name
    })

def question_detail(request, question_id):
    question = {
        'title': f'How to build a moon park? {question_id}',
        'id': question_id,
        'text': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit. Facere sunt reiciendis iure dolor ex, cumque laborum quibusdam repudiandae distinctio ipsum rem aut.',
        'rating': 5,
        'tags': ['black-jack', 'bender'],
    }
    
    answers = []
    for i in range(1, 15):
        answers.append({
            'id': i,
            'text': f'Answer #{i} to the question.',
            'rating': 8 - (i % 5),
            'is_correct': i == 3,
        })
    
    page = paginate(answers, request, 5)
    return render(request, 'question.html', {
        'question': question,
        'answers': page
    })

def login_view(request):
    return render(request, 'login.html')

def signup_view(request):
    return render(request, 'signup.html')

def ask_question(request):
    return render(request, 'ask.html')

def settings_view(request):
    return render(request, 'settings.html')