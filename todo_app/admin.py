from django.contrib import admin
from .models import Item

# Register your models here.
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['title','priority','date_created','date_due']
    list_filter = ['priority', 'date_created', 'date_due','completed']
    search_fields = ['title','priority']
    raw_id_fields = ['user']
    prepopulated_fields = {'slug':['title']}
    ordering = ['-priority','-title','-date_due']
