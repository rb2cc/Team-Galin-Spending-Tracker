from hitcount.utils import get_hitcount_model
from hitcount.views import HitCountMixin
from .models import Notification

# Utility method to update views on forum posts.
def update_views(request, object):
    context = {}
    hit_count = get_hitcount_model().objects.get_for_object(object)
    hits = hit_count.hits
    hitcontext = context["hitcount"] = {"pk":hit_count.pk}
    hit_count_response = HitCountMixin.hit_count(request, hit_count)

    if hit_count_response.hit_counted:
        hits = hits + 1
        hitcontext["hitcounted"] = hit_count_response.hit_counted
        hitcontext["hit_message"] = hit_count_response.hit_message
        hitcontext["total_hits"] = hits

# Utility method that creates notification to raise notifications.
def create_notification(request, to_user, notification_type, slug):
    notification = Notification.objects.create(to_user=to_user, notification_type=notification_type, created_by=request.user, slug=slug)

def create_achievement_notification(request, to_user, notification_type, achievement_type):
    notification = Notification.objects.create(to_user=to_user, notification_type=notification_type, created_by=request.user, achievement_type=achievement_type)