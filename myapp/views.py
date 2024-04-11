from django.shortcuts import render
from .models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone
from datetime import timedelta
from datetime import datetime
from pytz import timezone as timenewzone
def index(request):
    return render(request,'home.html')
def home(request):
    data={}
    data['questions']=Question.objects.all()
    for q in data['questions']:
        q.options=Option.objects.filter(question_id=q.question_id)
    return render(request,'home.html',data)
def create(request):
    data={}
    return render(request,'create.html')
def login(request):
    return render(request,'login.html')
def register(request):
    if request.method=='POST':
        ob=Userdetail()
        ob.username=request.POST['name']
        ob.email=request.POST['email']
        ob.password=request.POST['password']
        ob.save()
        return render(request,'login.html')
    return render(request,'register.html')
def vote(request,question_id):
    data={}
    data['question']=Question.objects.get(question_id=question_id)
    data['options']=Option.objects.filter(question_id=question_id)
    data['questionid']=question_id
    return render(request,'vote.html',data)
def result(request,question_id):
    totcnt=0
    winnerpoint=0
    winner=''
    data={}
    ques=Question.objects.get(question_id=question_id)
    result_date=ques.result_date
    ind_time = datetime.now(timenewzone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S.%f')
    cur_date = datetime.strptime(ind_time, '%Y-%m-%d %H:%M:%S.%f')
    current_date = timezone.now()
    time_to_add = timedelta(hours=5, minutes=30)
    current_date = current_date + time_to_add
    if current_date>result_date:
        data['isShowResult']=False
    else:
        data['result_date']=result_date
        data['isShowResult']=True
    data['question']=ques
    data['options']=Option.objects.filter(question_id=question_id)

    for i in data['options']:
        votecnt=Poll.objects.filter(question_id=question_id,option_id=i.option_id)
        optioncnt=len(votecnt)
        if winnerpoint<optioncnt:
            winnerpoint=optioncnt
            winner=i.option
        totcnt+=optioncnt
        i.cnt=optioncnt
    data['questionid']=question_id
    data['totalcount']=totcnt
    data['winner']=winner
    return render(request,'result.html',data)
@csrf_exempt 
def saveuser(request):
    if request.method=='POST':
        try:
            data = json.loads(request.body)
            email=data['email']
            password=data['password']
            user=Userdetail.objects.get(email=email,password=password)
            return JsonResponse({'user_id':user.user_id})
        except Exception as e:
            return JsonResponse({'error':'error'})
        return JsonResponse({'msg':'Hello'})
    return JsonResponse({'msg':'Hello'})
@csrf_exempt 
def createpoll(request):
    if request.method=='POST':
        try:
            data=json.loads(request.body)
            question=data['question']
            options=data['options']
            dateTime=data['datetime']
            datetime_obj = datetime.strptime(dateTime, '%Y-%m-%dT%H:%M')
            result_datetime= timezone.make_aware(datetime_obj, timezone.utc)
            questionob=Question()
            questionob.question=question
            questionob.result_date=result_datetime
            questionob.save()
            quID=questionob.pk
            for i in options:
                if i!='':
                    optionob=Option()
                    optionob.option=i
                    optionob.question_id=questionob
                    optionob.save()
        except Exception as e:
            print('err',e)   
    return JsonResponse({'created':True})

@csrf_exempt 
def savevote(request):
    if request.method=='POST':
        try:
            data=json.loads(request.body)
            userid=int(data['user_id'])
            option=data['option']
            questionid=int(data['question'])
            existvote=Poll.objects.filter(question_id=questionid,user_id=userid)
            ques=Question.objects.get(question_id=questionid)
            result_date=ques.result_date
            ind_time = datetime.now(timenewzone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S.%f')
            cur_date = datetime.strptime(ind_time, '%Y-%m-%d %H:%M:%S.%f')
            current_date = timezone.make_aware(cur_date, timezone.utc)
            print(current_date,result_date)
            if current_date>result_date:
                return JsonResponse({'status':2})
            isAlreadyVote=False
            if len(existvote)!=0:
                isAlreadyVote=True
                return JsonResponse({'status':0})
            pollob=Poll()
            optionob=Option.objects.get(option_id=option)
            user=Userdetail.objects.get(user_id=userid)
            questionob=Question.objects.get(question_id=questionid)
            pollob.option_id=optionob
            pollob.user_id=user
            pollob.question_id=questionob
            pollob.save()
            return JsonResponse({'status':1})
        except Exception as e:
            print('err',e)
    return JsonResponse({'status':0})