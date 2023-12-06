from django.urls import path
from .views import *

app_name = 'polling'
urlpatterns = [
    path('polling', index, name='polling'),
    path('<int:poll_id>/', detail, name='detail'),
    path('<int:poll_id>/results_api/',poll_results_api, name='poll_results_api'),
    path('add_question/', add_question, name='add_question'),
    path('<int:question_id>/add_choice/', add_choice, name='add_choice'),
    path('tong/', add_question_and_choices, name='add_question_and_choices'),
    path('view/poll/', view_poll_by_id, name='viewpoll'),
    path('voters/update', updateQuestion, name="updateQuestion"),
    path('rate/', rate, name='rate'),
    path('poll/<int:poll_id>/', option, name='poll_view'),
    path('present/<int:pk>', present, name='present'),
]