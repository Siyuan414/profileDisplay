from django.shortcuts import render,redirect
from .models import Profile
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm,ProfileForm,SkillForm,MessageForm
from .utils import searchProfiles, paginateProfiles
# Create your views here.
def loginUser(req):
    page = 'login'
    if req.user.is_authenticated:
        return redirect('profiles')
    
    if req.method == 'POST':
        username = req.POST['username'].lower()
        password = req.POST['password']
        
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(req,'Username does no exist')
        user = authenticate(req,username=username,password=password)
        
        if user is not None:
            login(req,user)
            return redirect(req.GET['next'] if 'next' in req.GET else 'account')
        else:
           messages.error(req,'username or password is not correct')
    return render(req,'users/login_register.html')

def logoutUser(req):
    logout(req)
    messages.info(req,'User was logged out')
    return redirect('login')

def registedUser(req):
    page = 'register'
    form = CustomUserCreationForm()
    
    if req.method == 'POST':
        form = CustomUserCreationForm(req.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            
            messages.success(req,'User account was created!')
            login(req,user)
            return redirect('edit-account')
        else:
            messages.error(req,'An error was occurred during registration')
    context = {'page':page,'form':form}
    return render(req,'users/login_register.html',context)

def profiles(req):
    profiles,search_query = searchProfiles(req)
    custom_range, profiles = paginateProfiles(req,profiles,1)
    context = {'profiles':profiles,'search_query':search_query,'custom_range':custom_range}
    return render(req,'users/profiles.html',context)

def userProfile(req,pk):
    
    profile = Profile.objects.get(id=pk)
    topSkills = profile.skill_set.exclude(description__exact="")
    otherSkills = profile.skill_set.filter(description="")
    context  = {'profile':profile,'topSkills':topSkills,'otherSkills':otherSkills}
    return render(req,'users/user-profile.html',context)

@login_required(login_url='login')
def userAccount(req):
    profile = req.user.profile
    topSkills = profile.skill_set.all()
    projects = profile.project_set.all()
    context  = {'profile':profile,'skills':topSkills,'projects':projects}
    return render(req,'users/account.html',context)

@login_required(login_url='login')
def editAccount(req):
    profile = req.user.profile
    form = ProfileForm(instance = profile)
    if req.method == 'POST':
        form = ProfileForm(req.POST,req.FILES,instance=profile)
        if form.is_valid():
            form.save()
            return redirect('account')
        
    context = {'form':form}
    return render(req,'users/profile_form.html',context)

@login_required(login_url='login')
def createSkill(req):
    profile = req.user.profile
    form = SkillForm()
    if req.method == 'POST':
        form = SkillForm(req.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = profile
            skill.save()
            messages.success(req,'Skill was successfully created')
            return redirect('account')
            
    context = {'form':form}
    return render(req,'users/skill_form.html',context)

@login_required(login_url='login')
def updateSkill(req,pk):
    profile = req.user.profile
    skill = profile.skill_set.get(id=pk)
    form = SkillForm(instance = skill)
    if req.method == 'POST':
        form = SkillForm(req.POST,instance=skill)
        if form.is_valid():
            form.save()
            messages.success(req,'Skill was successfully updated')
            return redirect('account')
    context = {'form':form}
    return render(req,'users/skill_form.html',context)

@login_required(login_url='login')
def deleteSkill(req,pk):
    profile = req.user.profile
    skill = profile.skill_set.get(id=pk)
    
    if req.method == 'POST':
        skill.delete()
        messages.success(req,'Skill was successfully deleted')
        return redirect('account')
    context = {'object':skill}
    return render(req,'delete_template.html',context)

@login_required(login_url='login')
def inbox(req):
    profile = req.user.profile
    messageRequests = profile.messages.all()
    unReadCount = messageRequests.filter(is_read=False).count()
    
    context = {'messageRequests':messageRequests,'unreadCount':unReadCount}
    return render(req,'users/inbox.html',context)

@login_required(login_url='login')
def viewMessage(req,pk):
    profile = req.user.profile
    message = profile.messages.get(id=pk)
    if message.is_read == False:
        message.is_read = True
        message.save()
        
    context = {'message':message}
    return render(req,'users/message.html',context)

@login_required(login_url='login')
def createMessage(req,pk):
    recipient = Profile.objects.get(id=pk)
    form = MessageForm()
    try:
        sender = req.user.profile
    except:
        sender = None
    
    if req.method == 'POST':
        form = MessageForm(req.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = sender
            message.recipient = recipient
            if sender:
                message.name = sender.name
                message.email = sender.email
            message.save()
            
            messages.success(req,"Your message was successfully sent!")
            return redirect('user-profile',pk=recipient.id)
    context = {'recipient':recipient, 'form':form}
    return render(req,'users/message_form.html',context)
        