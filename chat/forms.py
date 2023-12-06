from django import forms
from .models import Choice, Poll
from account.forms import FormSettings
from .models import AuthenticationMethod
from django import forms
from .models import Choice
from django.forms.models import ModelForm

class VoteForm(forms.Form):
    choice = forms.ChoiceField(widget=forms.RadioSelect,required = False)

    def __init__(self, poll_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = Choice.objects.filter(poll_id=poll_id)
        self.fields['choice'].choices = [(choice.id, choice.choice_text) for choice in choices]
        self.fields['choice'].label = ''
        
class PollForm(FormSettings):
    class Meta:
        model = Poll
        fields = ['question','pub_date']
        
        labels = {
            'question': 'Câu hỏi',
            'pub_date': 'Ngày biểu quyết',
        }
       
            

class ChoiceForm(ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text']
        error_messages = {
            'choice_text': {
                'required': 'Vui lòng chọn ít nhất 2 lựa chọn.',
            },
        }
        
        


