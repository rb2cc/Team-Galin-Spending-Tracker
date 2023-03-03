from .models import Expenditure

#Function that gets all expenditures that have is_binned field = True and deletes them all
def delete_old_expenditure_cron_job():
    binned_expenditures = Expenditure.objects.filter(is_binned=True)
    for expenditure in binned_expenditures:
        expenditure.delete()