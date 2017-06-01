# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.hashers import make_password , check_password
from .models import *
from .forms import *
from django.http import JsonResponse , HttpResponseRedirect
from json import JSONEncoder
from django.views.decorators.csrf import csrf_exempt
import uuid
from django.views.decorators.http import require_POST
from django.core.mail import send_mail

def CreateToken():
    newToken = str(uuid.uuid4())[:23].replace('-','').lower()
    try:
        tokenExists = members.objects.get(Token = newToken)
        # andMayBeHere = activation.objects.get(code = newToken)
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
    comments = Comment.objects.filter(active = True , post = post[0] )
    form  = form_comment(request.POST or None)
    if form.is_valid():
        Token = form.cleaned_data['Token']
        text = form.cleaned_data['Text']
        mmbr = members.objects.filter(Token = Token)
        post = Post.objects.filter(post_id = idd)
        new_comment , created = Comment.objects.get_or_create( member = mmbr , Text = text , post = post[0] )
    return render(request,'blog/post/detail.html',{'post':post[0],'comments':comments , 'form':form})



# ########## #
# App Views# #
# ########## #


@csrf_exempt
def Narlogin(request):
    email = request.POST['email']
    PassWord = request.POST['npass']
    user = members.objects.filter(email= email.lower() )
    if len(user)>0 and check_password(PassWord , user[0].password):
        if user[0].active:
            return JsonResponse({'Status':'0x0000','Token':user[0].Token, },encoder=JSONEncoder)
        else:
            return JsonResponse({'Status':'0x000F' },encoder=JSONEncoder)    
    else:
        return JsonResponse({'Status':'0x0001' },encoder=JSONEncoder)

@csrf_exempt
@require_POST
def NarSignUp(request):
    PassWord = make_password(request.POST['npass'], hasher='default')
    email    = request.POST['nemail']
    dispusn  = request.POST['ndispn']
    if PassWord and email  and dispusn :
        user = members.objects.filter(email= email.lower())
        if len(user)>0:
            return JsonResponse({'Status':'0x0002',},encoder=JSONEncoder)
        else:
            new_member , created = members.objects.get_or_create(
                email=email.lower() ,
                password = PassWord , 
                DisplayUserName = dispusn ,
                Token = CreateToken() )
            
            if created:
                code = CreateToken()
                actv = activation.objects.create(email = email , code = code)
                subject = 'فعال سازی اکانت ناردون'
                message = '{} .سلام {} عزیز, برای فعال سازی اکانت ناردون خود روی لینک زیر کلیک کنید. چنانچه شما در ناردون ثبت نام نکرده اید این ایمیل را نادیده بگیرید'.format(dispusn,request.build_absolute_uri('/activate/')+'?ac='+code)
                fmail = 'ali.jafari20@gmail.com'
                send_mail(subject, message, fmail,[email])
                try:
                    img = UploadProPicForm(request.POST, request.FILES)
                    if img.is_valid():
                        b4save = img.save(commit = False)
                        b4save.Token = new_member.Token
                        b4save.save()  
                        name, ext = str(request.FILES['propic']).replace(' ','_').split('.')
                        domain = "https://"+ request.get_host() +'/blog/static/media/usr/{}/profilepicture/profile.'.format(new_member.Token) + ext
                        new_member.ProPic = domain
                        new_member.save()
                except:
                    pass
                return JsonResponse({'Status':'0x0000',},encoder=JSONEncoder)
            else:
                return JsonResponse({'Status':'0x0003',}, encoder=JSONEncoder)
    else:
        return JsonResponse({'Status':'0x0006',}, encoder=JSONEncoder)


@csrf_exempt
def PostDetailView(request):
    postid = request.POST['id']
    post = Post.objects.filter(post_id = postid)
    if len(post)>0:
        result = dict()
        tmp = dict()
        coms = []
        comments = Comment.objects.filter(post = post[0] , active = True )
        if len(comments)>0:
            coms.clear()
            for cm in comments:
                response = dict()
                response.update({
                    'authorImg'    : str(cm.member.ProPic),
                    'Name'      : str(cm.member), 
                    'Text'      : cm.Text , 
                    'Date'      : str(cm.created.year)+'/'+str(cm.created.month)+'/'+str(cm.created.day) , 
                    'Time'      : str(cm.created.hour)+':'+str(cm.created.minute) 
                }) 
                coms.append(response)   
        result.update({'Comments':coms})
        return JsonResponse(result ,encoder=JSONEncoder)
    else:
        return JsonResponse({'Status':'0x000D'} ,encoder=JSONEncoder)

@csrf_exempt
def GroupPosts(request):
    gpname = request.POST['Group']
    group = NarGroups.objects.filter(Name = gpname)
    post = Post.objects.filter(Group = group , post_status = 'published' )
    result = dict()
    tmp = []
    i = len(post)
    for j in range(i-1,-1,-1):
        tpost = dict()
        tpost.update({
            'profile': str(post[j].author.ProPic),
            'Id'     : post[j].post_id , 
            'Image'  : post[j].ImageUrl ,
            'Title'  : post[j].Title ,
            'author' : post[j].author.DisplayUserName , 
            'Text'   : post[j].Text , 
            'Date'   : str(post[j].publish.year)+'/'+str(post[j].publish.month)+'/'+str(post[j].publish.day) , 
            'Time'   : str(post[j].publish.hour)+":"+str(post[j].publish.minute)
        }) 
        tmp.append(tpost)
    result.update({'Posts':tmp})
    return JsonResponse(result ,encoder=JSONEncoder)

@csrf_exempt
def fetchGroupNames(request):
    gp = NarGroups.objects.all()
    gps = []
    result = dict()
    if len(gp)>0:
        for g in gp:
            tmp = dict()
            tmp.update({ 
                'Name' : g.Name , 
                'logo' : g.logo
            })
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
        if str(user[0].AccessLevel) == 'admin':
            if name is not "" and desc is not "":
                ngr , created = NarGroups.objects.get_or_create(Name = name , description = desc)
                img = UploadlogoForm(request.POST, request.FILES)       
                if img.is_valid():
                    img.save()  
                    domain += request.get_host()
                    domain += "/blog/static/media/GroupLogo/" + str(request.FILES['pic']).replace(' ','_')
                    #TODO: rename uploaded image to a meaningful name !
                ngr.logo = domain
                ngr.save()
                return JsonResponse({'Status':'0x0000'} ,encoder=JSONEncoder)
            else:
                return JsonResponse({'Status':'0x0003'} ,encoder=JSONEncoder)
        else:
            return JsonResponse({'Status':'0x0007'} ,encoder=JSONEncoder)
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
        if mmber[0].AccessLevel != 'user':
            author = mmber[0]
            if Title is not "" and Text is not ""  and status is not "":
                if status is 'draft' or 'published':
                    chck = Post.objects.filter(author = author , Title = Title)
                    if len(chck)<1:
                        gp = request.POST['Group']
                        Group = NarGroups.objects.filter(Name = gp)
                        Today = datetime.datetime.now()
                        img = UploadPostImage_Form(request.POST, request.FILES)
                        domain = "https://"
                        if img.is_valid():
                            img.save()
                            domain += request.get_host()
                            domain += "/blog/static/media/post/{}/{}/{}/{}/{}/".format(Today.year,Today.ctime()[4:7],Today.day,Today.hour,Today.minute) + str(request.FILES['Image']).replace(' ','_')
                        pst = Post.objects.create(post_status = status ,Title = Title , author = author , Text = Text , ImageUrl=domain ,Group = Group[0] ,publish = Today)
                        return JsonResponse({'Status':'0x0000'} ,encoder=JSONEncoder)
                    else:
                        return JsonResponse({'Status':'0x0005'} ,encoder=JSONEncoder)
                else:
                    return JsonResponse({'Status':'0x000C'} ,encoder=JSONEncoder)
            else:
                return JsonResponse({'Status':'0x0006'} ,encoder=JSONEncoder)
        else:
            return JsonResponse({'Status':'0x0007'} ,encoder=JSONEncoder)
    else:
        return JsonResponse({'Status':'0x0004'} ,encoder=JSONEncoder)

@csrf_exempt
def addcomment(request):
    post_id = request.POST['PostId']
    Token = request.POST['Token']
    Text = request.POST['Text']
    user = members.objects.filter(Token = Token)
    post = Post.objects.filter(post_id = post_id)
    if len(user)>0:
        if len(post)>0:
            if Text != "":
                Comment.objects.get_or_create(post = post[0] , member = user[0] , Text = Text)
                return JsonResponse({'Status':'0x0000' },encoder=JSONEncoder)
            else:
                return JsonResponse({'Status':'0x0006' },encoder=JSONEncoder)
        else:
            return JsonResponse({'Status':'0x0008' },encoder=JSONEncoder)
    else:
        return JsonResponse({'Status':'0x0001' },encoder=JSONEncoder)

@csrf_exempt
def getAvailableGroups(request):
    Email = request.POST['Email']
    user = members.objects.filter(email = Email)
    res = dict()
    arr = []
    if len(user)>0:
        if user[0].AccessLevel == 'user':
            return JsonResponse({'Status':'0x0007'},encoder=JSONEncoder)
        elif user[0].AccessLevel == 'member':
            gp = GroupMembers.objects.filter(user = user[0])
            for n in gp :
                tmp = dict()
                tmp.update({'Name':str(n.group) , 'Logo':n.logo})
                arr.append(tmp)    
        elif user[0].AccessLevel == 'admin':
            ng = NarGroups.objects.all()
            for n in ng :
                tmp = dict()
                tmp.update({'Name':n.Name, 'Logo':n.logo})
                arr.append(tmp)
    else:
        return JsonResponse({'Status':'0x0004'},encoder=JSONEncoder)
    res.update({'Groups':arr})
    return JsonResponse(res,encoder=JSONEncoder)

@csrf_exempt
def setAvailableGroups(request):
    Token = request.POST['Token']
    admin = members.objects.filter(Token = Token)
    if len(admin)>0:
        if admin[0].AccessLevel != 'admin':
            return JsonResponse({'Status':'0x0007'},encoder=JSONEncoder)
        else:
            un = request.POST['email']
            gp = request.POST['group']
            action = request.POST['action']
            if un != "" and gp != "":
                user = members.objects.filter(email = un)
                group = NarGroups.objects.filter(Name = gp)
                if len(user)>0:
                    if len(group)>0:
                        if action == 'add':
                            GroupMembers.objects.get_or_create(user = user[0] , group = group[0])
                            return JsonResponse({'Status':'0x0000'},encoder=JSONEncoder)
                        elif action == 'remove':
                            x = GroupMembers.objects.filter(user = user[0] , group = group[0])
                            x.delete()
                            return JsonResponse({'Status':'0x0000'},encoder=JSONEncoder)
                        else:
                            return JsonResponse({'Status':'0x000B'},encoder=JSONEncoder)
                    else:
                        return JsonResponse({'Status':'0x000A'},encoder=JSONEncoder)
                else:
                    return JsonResponse({'Status':'0x0009'},encoder=JSONEncoder)   
            else:
                 return JsonResponse({'Status':'0x0006'},encoder=JSONEncoder)
    else:
        return JsonResponse({'Status':'0x0004'},encoder=JSONEncoder)

@csrf_exempt
def App_LoadProfile(request):
    Token = request.POST['Token']
    user = members.objects.filter(Token = Token)
    if len(user)>0:
        u = user[0]
        res = {'propic':u.ProPic ,'Email':u.email , 'dispun':u.DisplayUserName , 'AccessLevel':u.AccessLevel}
        return JsonResponse(res,encoder=JSONEncoder)
    else:
        return JsonResponse({'Status':'0x0004'},encoder=JSONEncoder)


@csrf_exempt
def App_MemberProfileView(request):
    postID = request.POST['postid']
    if postID != "":
        post = Post.objects.get(post_id = postID)
        u = post.author
        gps = GroupMembers.objects.filter(user = u)
        grp = []
        for g in gps:
            groups = dict()
            groups.update({'Name':g.group})
            grp.append(groups)
        res = {'propic':u.ProPic ,'Email':u.email , 'dispun':u.DisplayUserName , 'AccessLevel':u.AccessLevel , 'Groups':grp}
        return JsonResponse(res,encoder=JSONEncoder)
    else:
        return JsonResponse({'Status':'0x0006'},encoder=JSONEncoder)

@csrf_exempt
def App_EditProfile(request):
    Token = request.POST['Token']
    user = members.objects.filter(Token = Token)
    if len(user)>0:
        u = user[0]
        res = dict()
        arr = []
        try:
            img = UploadProPicForm(request.POST , request.FILES)  
            if img.is_valid():
                s = img.save(commit = False)
                s.Token = Token
                s.save()
                name, ext = str(request.FILES['propic']).replace(' ','_').split('.')
                u.propic = "https://"+ request.get_host() +'/blog/static/media/usr/{}/profilepicture/profile.'.format(Token) + ext
                tmp = {'Status':'0x0000'}
                arr = []
                arr.append(tmp)
                res.update({'ProfilePicture':arr})
        except:
            tmp = {'Status':'0x0000'}
            arr.append(tmp)
            res.update({'ProfilePicture':arr})
            
        try:
            newEmail = request.POST['email']
            if newEmail == "":
                tmp = {'Status':'0x0006'}
                arr = []
                arr.append(tmp)
                res.update({'Email':arr})
            else:
                chk = members.objects.filter(email = newEmail)
                if len(chk)>0:
                    tmp = {'Status':'0x0002'}
                    arr = []
                    arr.append(tmp)
                    res.update({'Email':arr})
                else:
                    u.email = newEmail
                    tmp = {'Status':'0x0000'}
                    arr = []
                    arr.append(tmp)
                    res.update({'Email':arr})

        except:
            pass
        try:
            dispn = request.POST['dispun']
            if dispn == "":
                tmp = {'Status':'0x0006'}
                arr = []
                arr.append(tmp)
                res.update({'DisplayUName':arr})
            else:
                u.dispun = request.POST['dispun']
                tmp = {'Status':'0x0000'}
                arr = []
                arr.append(tmp)
                res.update({'DisplayUName':arr})
        except:
            pass
        try:
            if check_password(request.POST['OldPass'] , p.password):
                pwd = request.POST['NewPass']
                if pwd == "":
                    tmp = {'Status':'0x0006'}
                    arr = []
                    arr.append(tmp)
                    res.update({'PassWord':arr})
                else:
                    u.password = make_password(request.POST['NewPass'] , hasher='default')
                    tmp = {'Status':'0x0000'}
                    arr = []
                    arr.append(tmp)
                    res.update({'PassWord':arr})
            else:
                tmp = {'Status':'0x000E'}
                arr = []
                arr.append(tmp)
                res.update({'PassWord':arr})
        except:
            pass
        u.save()
        return JsonResponse(res,encoder=JSONEncoder)
    else:
        return JsonResponse({'Status':'0x0004'},encoder=JSONEncoder)

        
def activate(request):
    code = request.GET['ac']
    req = activation.objects.filter(code = code)
    if len(req)>0 :  # if code is in temporary db, read the data and create the user
        mmbr = members.objects.get(email = req[0].email)
        mmbr.active = True
        mmbr.save()
        req[0].delete()
        return JsonResponse({'message':'ok'},encoder=JSONEncoder)
    else:
        return JsonResponse({'message':'ridi'},encoder=JSONEncoder)
