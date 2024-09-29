from django.shortcuts import render,redirect
from django.http import HttpResponse
# Create your views here.
from django.http import HttpResponse
from .models import Project,Tag
from .forms import ProjectForm, ReviewForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .utils import searchProjects,paginateProjects

def projects(req):
    projects, search_query = searchProjects(req)
    custom_range, projects = paginateProjects(req,projects,3)
    context = {"projects":projects,'search_query':search_query,'custom_range':custom_range}
    return render(req,'projects/projects.html',context)

def project(req,pk):
    projectObj = Project.objects.get(id=pk)
    form = ReviewForm()
    if req.method == 'POST':
        form = ReviewForm(req.POST)
        review = form.save(commit=False)
        review.project = projectObj
        review.owner = req.user.profile
        review.save()
        projectObj.getVoteCount
        messages.success(req,'Your review is already submitted!')
        return redirect('project',pk=projectObj.id)
    return render(req,'projects/single_project.html',{'project':projectObj,'form':form})

@login_required(login_url='login')
def createProject(req):
    profile = req.user.profile
    form = ProjectForm()
    if req.method == 'POST':
        form = ProjectForm(req.POST,req.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = profile
            project.save()
            return redirect('account')
    
    context = {'form':form}
    return render(req,"projects/project_form.html",context)

@login_required(login_url='login')
def updateProject(req,pk):
    profile = req.user.profile
    project = profile.project_set.get(id=pk)
    form = ProjectForm(instance=project)
    
    if req.method == 'POST':
        newtags = req.POST.get('newtags').replace(',',' ').split()
        form = ProjectForm(req.POST,req.FILES,instance=project)
        if form.is_valid():
            form.save()
            for tag in newtags:
                tag,created = Tag.objects.get_or_create(name=tag)
                project.tags.add(tag)
            return redirect('account')
    context = {'form':form}
    return render(req,"projects/project_form.html",context)

@login_required(login_url='login')
def deleteProject(req,pk):
    profile = req.user.profile
    project = profile.project_set.get(id=pk)
    if req.method == 'POST':
        project.delete()
        return redirect('projects')
    context = {'object':project}
    return render(req,'delete_template.html',context)