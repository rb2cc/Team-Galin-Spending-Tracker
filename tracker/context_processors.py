from .models import Post
from .models import Notification

# Allows search function to find objects which contain keywords.

def searchFunction(request):

    context = {}

    posts = Post.objects.all()

    if "search" in request.GET:
        query = request.GET.get("q")
    
        #Filter Begins
        search_box = request.GET.get("search-box")
        if search_box == "Descriptions":
            objects = posts.filter(content__icontains=query)
        else:
            objects = posts.filter(title__icontains=query)
        #Filter Ends

    
        context = {
            "objects": objects,
            "query": query,

    }
    return context
        
# Allows notifications that have not been read to be returned.

def notifications(request):
    if request.user.is_authenticated:
        return {'notifications': request.user.notifications.filter(is_read=False)
    }
    else:
        return  {'notifications': []}