from django.core.management.base import BaseCommand
from tracker.models import Expenditure, Category, User
from django.utils import timezone
from dateutil.relativedelta import relativedelta, MO, SU
from tracker.send_emails import Emailer

class Command(BaseCommand):

    def handle(self, *args, **options):
            
        """Code below that will go through expenditures and categories with is_binned=True and deletes them all"""
        
        binned_expenditures = Expenditure.objects.filter(is_binned=True)
        binned_categories = Category.objects.filter(is_binned=True)
        
        for expenditure in binned_expenditures:
            expenditure.delete()
            
        for category in binned_categories:
            category.delete()
            
        """Code below that will send an email to the user when one of their categories is close to their weekly limit"""
        """Limits the emails being sent to only when spending >=90% and has_email_sent=False to not fill up email inbox"""
        
        def _make_percent(num, cat_name, user):
                    denom = Category.objects.filter(users__id = user.id).get(name=cat_name).week_limit
                    percent = (100 * (float(num)/float(denom)))
                    if percent > 100:
                        return 100
                    return percent

        for user in User.objects.filter(is_staff=False, is_superuser=False):
            
            week_start = timezone.now().date() + relativedelta(weekday=MO(-1))
            week_end = week_start + relativedelta(weekday=SU(1)) 
            categories = Category.objects.filter(is_overall = False).filter(users__id = user.id)
            val_dict = {}
            for category in categories:
                val_dict[category.name] = 0 
            expenditures = Expenditure.objects.filter(user=user, date_created__gte = week_start, date_created__lte = week_end, is_binned = False)
            for expenditure in expenditures:
                val_dict[expenditure.category.name] += expenditure.expense#dict from category name -> total expense
            overall_spend = sum(val_dict.values())
            overall = Category.objects.filter(users__id = user.id, is_overall=True)
            overall_percent = _make_percent(overall_spend, overall.get(name="Overall"), user)

            if overall_percent >= 90 and not user.has_email_sent:
                user.has_email_sent = True
                user.save()
                Emailer.send_spending_limit_notification("Spending Limits", user.email, user.first_name)
            elif overall_percent < 90 and  user.has_email_sent:
                user.has_email_sent = False
                user.save()
            else: 
                pass

