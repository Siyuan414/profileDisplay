from django.db.models import Q
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from .models import Project, Tag
def searchProjects(req):
    search_query = req.GET.get('search_query') if req.GET.get('search_query') else '' 
    tags = Tag.objects.filter(name__icontains = search_query)
    projects = Project.objects.distinct().filter(
        Q(title__icontains = search_query) | 
        Q(description__icontains = search_query) |
        Q(owner__name__icontains = search_query) | 
        Q(tags__in=tags)
    )
    return projects,search_query

def paginateProjects(req,projects,results):
    page = req.GET.get('page')
    paginator  = Paginator(projects,results)
    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        projects = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        projects = paginator.page(page)
    
    leftIndex = (int(page) - 4)
    if leftIndex < 4:
        leftIndex = 1
    rightIndex = (int(page) + 5)
    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages + 1
    custom_range = range(leftIndex,rightIndex)
    return custom_range, projects