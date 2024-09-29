from django.db.models import Q
from .models import Profile,Skill
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage

def searchProfiles(req):
    search_query = req.GET.get('search_query') if req.GET.get('search_query') else '' 
    skills = Skill.objects.filter(name__icontains = search_query)
    profiles = Profile.objects.distinct().filter(
        Q(name__icontains = search_query) | 
        Q(short_intro__icontains = search_query) |
        Q(skill__in=skills)
    )
    return profiles,search_query

def paginateProfiles(req,profiles,results):
    page = req.GET.get('page')
    paginator  = Paginator(profiles,results)
    try:
        profiles = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        profiles = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        profiles = paginator.page(page)
    
    leftIndex = (int(page) - 4)
    if leftIndex < 4:
        leftIndex = 1
    rightIndex = (int(page) + 5)
    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages + 1
    custom_range = range(leftIndex,rightIndex)
    return custom_range, profiles