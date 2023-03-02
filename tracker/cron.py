from .models import Expenditure

def delete_old_expenditure_cron_job():
    binned_expenditures = Expenditure.objects.filter(is_binned=True)
    for expenditure in binned_expenditures:
        expenditure.delete()