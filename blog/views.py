# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from .models import *
from .forms import *
from django.http import JsonResponse , HttpResponseRedirect
from json import JSONEncoder
from django.views.decorators.csrf import csrf_exempt
import uuid
from django.views.decorators.http import require_POST

def CreateToken():
    newToken = str(uuid.uuid4())[:23].replace('-','').lower()
    try:
        tokenExists = members.objects.get(Token = newToken)
        CreateToken()
    except:
        return newToken

def post_list(request):
    posts = Post.objects.filter(post_status = "published")
    return render(request , 'blog/post/list.html' , {'posts':posts})

def singup(request):
    form = form_SignUp()
    return render(request , "blog/base.html" , {"form":form})

def addGroupform(request):
    form = form_Group()
    # if form.is_valid():
    return render(request , "blog/base.html" , {"form":form})
    
def post_detail(request,idd):
    post = Post.objects.filter(post_id = idd)
    comments = Comment.objects.filter(active = True , postID = post[0].post_id )
    form  = form_comment(request.POST or None)
    if form.is_valid():
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        text = form.cleaned_data['Text']
        postid = Post.objects.filter(post_id = idd)
        new_comment , created = Comment.objects.get_or_create(email=email , name = name , Text = text , postID = postid[0] )
    return render(request,'blog/post/detail.html',{'post':post[0],'comments':comments , 'form':form})



# ########## #
# App Views# #
# ########## #


@csrf_exempt
def Narlogin(request):
    UserName = request.POST['nuser']
    PassWord = request.POST['npass']
    user = members.objects.filter(userName= UserName.lower() ,password = PassWord)
    if len(user)>0:
        return JsonResponse({'Status':'0x0000','Token':user[0].Token, },encoder=JSONEncoder)
    else:
        return JsonResponse({'Status':'0x0001' },encoder=JSONEncoder)

@csrf_exempt
@require_POST
def NarSignUp(request):
    UserName = request.POST['nuser']
    PassWord = request.POST['npass']
    email    = request.POST['nemail']
    dispusn  = request.POST['ndispn']
    grp      = request.POST['ngroup']
    #TODO: check if any empty parameters passed, return Error!
    ngroup = NarGroups.objects.filter(Name = grp)

    user = members.objects.filter(userName= UserName.lower())
    if len(user)>0:
        return JsonResponse({'Status':'0x0002',},encoder=JSONEncoder)
    else:
        new_member , created = members.objects.get_or_create(email=email , userName = UserName.lower() , password = PassWord , DisplayUserName = dispusn , Group = ngroup[0] , Token = CreateToken() )
        if created:
            return JsonResponse({'Status':'0x0000',},encoder=JSONEncoder)
        else:
            return JsonResponse({'Status':'0x0003',}, encoder=JSONEncoder)


@csrf_exempt
def PostDetailView(request):
    postid = request.POST['id']

    post = Post.objects.filter(post_id = postid)
    result = dict()
    tmp = dict()
    coms = []
    comments = Comment.objects.filter(postID = post[0] , active = True )
    if len(comments)>0:
        coms.clear()
        for cm in comments:
            response = dict()
            response.update({'Name' : cm.name , 'Text' : cm.Text , 'Date' : str(cm.created.year)+'/'+str(cm.created.month)+'/'+str(cm.created.day) , 'Time' : str(cm.created.hour)+':'+str(cm.created.minute) }) 
            coms.append(response)   
    result.update({'Comments':coms})
    return JsonResponse(result ,encoder=JSONEncoder)

@csrf_exempt
def GroupPosts(request):
    gpname = request.POST['Group']
    group = NarGroups.objects.filter(Name = gpname)
    post = Post.objects.filter(Group = group , post_status = 'published' )  #TODO: add status = Published condition
    result = dict()
    tmp = []
    i = len(post)
    for j in range(i-1,-1,-1):
        tpost = dict()
        tpost.update({'Id': post[j].post_id , 'Image':post[j].ImageUrl ,'Title':post[j].Title , 'author' : post[j].author.DisplayUserName , 'Text':post[j].Text , 'Date': str(post[j].publish.year)+'/'+str(post[j].publish.month)+'/'+str(post[j].publish.day) , 'Time': str(post[j].publish.hour)+":"+str(post[j].publish.minute) }) 
        tmp.append(tpost)
    result.update({'Posts':tmp})
    return JsonResponse(result ,encoder=JSONEncoder)

@csrf_exempt
def fetchGroupNames(request):
    gp = NarGroups.objects.all()
    if len(gp)>0:
        result = dict()
        gps = []
        for g in gp:
            tmp = dict()
            tmp.update({ 'Name' : g.Name , 'logo':g.logo })
            gps.append(tmp)
        result.update({'Groups':gps})
        return JsonResponse(result ,encoder=JSONEncoder)


@csrf_exempt
def addGroup(request):
    name = request.POST['Name'] 
    desc = request.POST['description']
    Token = request.POST['Token']
    user = members.objects.filter(Token = Token)
    if len(user) > 0:
        if name is not "" and desc is not "":
            ngr , created = NarGroups.objects.get_or_create(Name = name , description = desc)
            img = UploadlogoForm(request.POST, request.FILES)       
            domain = "https://"
            if img.is_valid():
                img.save()  
                domain += request.get_host()
                domain += "/blog/static/media/GroupLogo/" + str(request.FILES['pic'])
                #TODO: rename uploaded image to a meaningful name !
            ngr.logo = domain
            ngr.save()
            return JsonResponse({'Status':'0x0000'} ,encoder=JSONEncoder)
        else:
            return JsonResponse({'Status':'0x0003'} ,encoder=JSONEncoder)
    else:
        return JsonResponse({'Status':'0x0004'} ,encoder=JSONEncoder)

@csrf_exempt
def addNewPost(request):
    Token = request.POST['Token']
    Title = request.POST['Title']
    Text = request.POST['Text']
    status = request.POST['status']
    mmber = members.objects.filter(Token = Token)
    if len(mmber)>0:
        author = mmber[0]
        if Title is not "" and Text is not "":
            chck = Post.objects.filter(author = author , Title = Title)
            if len(chck)<1:
                gp = request.POST['Group']
                Group = NarGroups.objects.filter(Name = gp)
                Today = datetime.datetime.now()
                img = UploadPostForm(request.POST, request.FILES)
                domain = "https://"
                if img.is_valid():
                    img.save()
                    domain += request.get_host()
                    domain += "blog/satic/media/post/{}/{}/{}/{}/{}".format(Today.year,Today.month,Today.day,Today.hour,Today.minute) + str(request.FILES['Image'])
                pst = Post.objects.create(post_status = status ,Title = Title , author = author , Text = Text , ImageUrl=domain ,Group = Group[0] ,publish = Today)
                return JsonResponse({'Status':'0x0000'} ,encoder=JSONEncoder)
            else:
                return JsonResponse({'Status':'0x0005'} ,encoder=JSONEncoder)
        else:
            return JsonResponse({'Status':'0x0006'} ,encoder=JSONEncoder)
    else:
        return JsonResponse({'Status':'0x0004'} ,encoder=JSONEncoder)