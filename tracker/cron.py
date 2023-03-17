from .models import Expenditure, Category

#Function that gets all expenditures that have is_binned field = True and deletes them all
def delete_binned_objects_cron_job():
    binned_expenditures = Expenditure.objects.filter(is_binned=True)
    binned_categories = Category.objects.filter(is_binned=True)
    
    for expenditure in binned_expenditures:
        expenditure.delete()
        
    for category in binned_categories:
        category.delete()