from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
import datetime

# Create your models here.
# class List(models.Model):
#     title = models.CharField(max_length=120,unique=True)

#     def __str__(self):
#         return self.title
    
#     class Meta:
#         ordering = ['title']

class Item(models.Model):
    PRIORITY = (
        ('high','high'),
        ('medium','medium'),
        ('low','low')
    )
    title = models.CharField(max_length=120)
    date_created = models.DateField(auto_now_add=True,db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='tasks')
    slug = models.SlugField(unique_for_date='date_created',max_length=200)
    date_due = models.DateField(default=timezone.now)
    priority = models.CharField(max_length=6,choices=PRIORITY,default='medium')
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    expired = models.BooleanField(default=False)


    class Meta:
        ordering = ['-priority','date_due','title']
        unique_together = ('slug','date_created','user')
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Item, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('detail',args=[self.id,self.slug])

    def __str__(self):
        return self.title
    
    def expired(self):
        if datetime.date.today() > self.date_due:
            return True



