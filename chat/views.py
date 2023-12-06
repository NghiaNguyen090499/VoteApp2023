from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum
from django.contrib import messages
from .models import *
from .forms import *
from .models import AuthenticationMethod
from django.views.generic import TemplateView
from django.views import View
import qrcode
import qrcode.image.svg
from io import BytesIO
from django.conf import settings
from qrcode import make

def index(request):
    latest_polls = Poll.objects.order_by('-pub_date')[:5]
    context = {'latest_polls': latest_polls}
    return render(request, 'chat/index.html', context)


def add_question(request):
    if request.method == 'POST':
        form = PollForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('polling:question_list')
    else:
        form = PollForm()
    return render(request, 'chat/add_question.html', {'form': form})

def add_choice(request, question_id):
    question = get_object_or_404(Poll, pk=question_id)
    if request.method == 'POST':
        form = ChoiceForm(request.POST)
        if form.is_valid():
            choice = form.save(commit=False)
            choice.question = question
            choice.save()
            return redirect('polling:question_detail', question_id=question.id)
    else:
        form = ChoiceForm()
    return render(request, 'chat/add_choice.html', {'form': form, 'question': question})

def detail(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    total_votes = poll.choice_set.aggregate(Sum('votes'))['votes__sum']
    form = VoteForm(poll_id, request.POST)
    
    if request.method == 'POST':
        form = VoteForm(poll_id, request.POST)
        if form.is_valid():
            choice_id = form.cleaned_data['choice']
            choice = get_object_or_404(Choice, pk=choice_id)
            choice.votes += 1
            choice.save()
            messages.success(request, "Thank you for voting!")
            return HttpResponse('Cám ơn bạn đã đánh giá')
    else:
        form = VoteForm(poll_id)

    return render(request, 'chat/detail.html', {'poll': poll, 'total_votes': total_votes, 'form': form})

def poll_results_api(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    total_votes = poll.choice_set.aggregate(Sum('votes'))['votes__sum']
    results = [{'choice_text': choice.choice_text, 'votes': choice.votes} for choice in poll.choice_set.all()]
    return JsonResponse({'results': results, 'total_votes': total_votes})



def add_question_and_choices(request):
    form = AuthForm
    if request.method == 'POST':
        # Xử lý form câu hỏi
        question_form = PollForm(request.POST)
        if question_form.is_valid():
            question_instance = question_form.save()
            # Xử lý form xác thực
            auth_form = AuthForm(request.POST)
            if auth_form.is_valid():
                selected_methods = auth_form.cleaned_data['authentication_methods']

                # Liên kết các phương thức xác thực với câu hỏi
                question_instance.authentication_methods.set(selected_methods)

                # Xử lý form lựa chọn
                choice_forms = [ChoiceForm({'choice_text': choice_text}) for choice_text in request.POST.getlist('choices[]')]
                choice_forms = [choice_form for choice_form in choice_forms if choice_form['choice_text'].value()]

                if all(choice_form.is_valid() for choice_form in choice_forms):
                    # Process and save the choices
                    for choice_form in choice_forms:
                        choice_text = choice_form.cleaned_data.get('choice_text', '')
                        Choice.objects.create(choice_text=choice_text, poll=question_instance)
                        print(question_instance.id)
                        context = {}
                        url = reverse('polling:poll_view',args=[question_instance.id])
                        print(url)
                        
                        data = f"http://192.168.15.174:8000/{url}"
                        
                        img = make(data)

                        img_name = f'{question_instance.id}.png'
                        img.save(settings.MEDIA_ROOT + '/' + img_name)
                        context = {
                                'img_name': img_name
                            }
                            
                    return redirect('success_page')  # Redirect to a success page or any other page


            return redirect('success_page')  # Redirect to a success page or any other page

        else:
            # Print errors for debugging
            for choice_form in choice_forms:
                print(choice_form.errors)
    else:
        question_form = PollForm()
        choice_forms = [ChoiceForm(prefix=str(i)) for i in range(3)]
    
    questions=Poll.objects.all()
    
   

    return render(request, 'chat/polling.html', {'question_form': question_form, 'choice_forms': choice_forms,'questions':questions,'form':form})


def view_poll_by_id(request):
    pollid = request.GET.get('id', None)
    print(pollid)
    context = {}
    poll = Poll.objects.get(id=pollid)
    choices = Choice.objects.filter(poll_id=pollid)
    # Lấy thông tin câu hỏi
    context = {
        'id': poll.id,
        'question': poll.question,
        'pub_date': poll.pub_date,
    }
    
    print(context)
    # Lấy thông tin các câu trả lời (choices)
    context['choices'] = [
        {
            'id': choice.poll_id,
            'choice_text': choice.choice_text,
            'votes': choice.votes,
        }
        for choice in choices
    ]
    print(context['choices'])

    context['code'] = 200


    return JsonResponse(context)

def updateQuestion(request):
    
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        instance = Poll.objects.get(id=request.POST.get('id'))
        choice_forms = [ChoiceForm({'choice_text': choice_text}) for choice_text in request.POST.getlist('choices[]')]
        voter = PollForm(request.POST or None, instance=instance)
        voter.save()
        messages.success(request, "Voter's bio updated")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('adminViewVoters'))


def rate(request):
    
    if request.method == 'POST':
        form = AuthForm(request.POST)
        if form.is_valid():
            print(form)
            
            pass
            # Xử lý dữ liệu form ở đây
    else:
        form = AuthForm()


    # Truyền form vào context để hiển thị trong template
    return render(request, 'chat/rate.html', {'form': form})
  
  
  
def option(request,poll_id):
    poll_instance = get_object_or_404(Poll, id=poll_id)
    authentication_methods = poll_instance.authentication_methods.all()
    for method in authentication_methods:
        print(method.id)
        if method.id == 1:
            print('a')
            if request.method == 'POST' :
                print(poll_id)
                myfile = request.FILES['myfile']
                print(myfile)
                url=reverse('polling:detail',args=[poll_id])
                print(url)
                
                return redirect(url)
            return render(request, 'chat/upload_cccd.html', {'poll': poll_instance})
        elif method.id == 2:
            return render(request, 'chat/input_id.html', {'poll': poll_instance})
        else:
            return render(request, 'chat/options.html', {'poll': poll_instance})
            
            
            
    
def present(request,pk):
    poll_instance = get_object_or_404(Poll, id=pk)
    poll =Poll.objects.get(id=pk)
    context = {}
    url = reverse('polling:poll_view',args=[pk])
    print(url)
    data = f"http://192.168.15.174:8000{url}"
    img = make(data)

    img_name = f'{pk}.png'
    img.save(settings.MEDIA_ROOT + '/' + img_name)
    context = {
            'img_name': img_name
        }
        
    print(poll)
    return render(request, 'chat/present.html', {'poll':poll,'img_name':img_name})