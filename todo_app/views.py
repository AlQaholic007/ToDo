from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import LoginForm,UserRegistrationForm,UserEditForm,TaskCreateForm,EmailForm,TaskEditForm
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from .models import Item
import datetime
from django.db import IntegrityError
from django.urls import reverse
from django.core.mail import send_mail
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.views.generic.edit import UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q


# Create your views here.
# def user_login(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             user = authenticate(request,username = cd['username'],password = cd['password'])

#             if user is not None:
#                 if user.is_active:
#                     login(request,user)
#                     return HttpResponse('Authentication successful!')
#                 else:
#                     return HttpResponse('User not active!')
#             else:
#                 return HttpResponse('Authentication failed! Invalid Login.')
#     else:
#         form = LoginForm()

#     return render(request,'auth/login.html',{'form': form,'title':'Login'})


class ItemUpdate(LoginRequiredMixin,SuccessMessageMixin,UpdateView):
    model = Item
    form_class = TaskEditForm
    template_name = 'tasks/edit.html' 
    success_url = '/dashboard/'
    success_message = 'Task updated successfully!'
    
    def form_valid(self, form):
        try:
            return super(ItemUpdate, self).form_valid(form)
        except IntegrityError:
            messages.error(self.request,'Failed to update. Repititive tasks on the same day!')
            return redirect('dashboard')

@login_required
def dashboard(request,task_filter=None):
    # if view_completed:
    #     tasks = Item.objects.filter(user=request.user,completed=True)
    # else:
    #     tasks = Item.objects.filter(user=request.user)
    if task_filter == "completed":
        task_list = Item.objects.filter(user=request.user,completed = True)
    elif task_filter == "expired":
        task_list = Item.objects.filter(user=request.user)
        ids = [task.id for task in task_list if task.expired()]
        task_list = task_list.filter(id__in=ids)
    elif task_filter == "incomplete":
        task_list = Item.objects.filter(user=request.user,completed = False)
        ids = [task.id for task in task_list if not task.expired()]
        task_list = task_list.filter(id__in=ids)
    elif task_filter == "search":
        query = self.request.GET.get('q')
        if query:
            task_list = Item.objects.filter(Q(title__icontains=query),Q(user=request.user))
        else:
            task_list = Item.objects.filter(user=request.user)
    else:
        task_list = Item.objects.filter(user=request.user)
    
    paginator = Paginator(task_list,4)
    page = request.GET.get('page')
    try:
        tasks = paginator.page(page)
    except PageNotAnInteger:
        tasks = paginator.page(1)
    except EmptyPage:
        tasks = paginator.page(paginator.num_pages)
    
    return render(request,"account/dashboard.html",{'section':'dashboard','tasks':tasks,'page':page})

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(
                user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            # Create the user profile
            return render(request,
                          'account/register_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'account/register.html',
                  {'user_form': user_form})

@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,data=request.POST)
        if user_form.is_valid():
            user_form.save()
            messages.success(request,'Profile updated successfully')
        else:
            messages.error(request,'Error updating your profile')

    else:
        user_form = UserEditForm(instance=request.user)
    
    return render(request,'account/edit.html',{'user_form':user_form,'section':'edit'})

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskCreateForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_task = form.save(commit=False)
            new_task.user = request.user
            try:
                new_task.save()
            except IntegrityError:
                messages.error(request,'Repititive tasks on the same day!')
                return redirect('/create/')
            messages.success(request,'Task added successfully')

            return redirect(new_task.get_absolute_url())
    else:
        form = TaskCreateForm()

    return render(request,'tasks/create.html',{'form':form,'section':'tasks'})

@login_required
def task_detail(request,id,slug):
    task = get_object_or_404(Item,id=id,slug=slug)

    # if request.method == 'POST':
    #     form = TaskCreateForm(request.POST)
    #     if form.is_valid():
    #         cd = form.cleaned_data
    #         for key in cd.keys():
    #             if cd[key]:
    #                 if key=='title':
    #                     task.title = cd[key]
    #                 elif key=='date_due':
    #                     task.date_due = cd[key]
    #                 elif key=='priority':
    #                     task.priority = cd[key]
    #                 else:
    #                     task.description = cd[key]
    #         try:
    #             task.save()
    #         except IntegrityError:
    #             messages.error(request,'Repititive tasks on the same day!')
    #             return redirect('/dashboard/')

    #         messages.success(request,'Task updated successfully.')
    #         return redirect('dashboard')
    # else:
    #     form = TaskCreateForm()
    return render(request,'tasks/detail.html',{'section':'tasks','task':task})

@login_required
def toggle_task(request,id):
    task = Item.objects.get(pk=id)
    task.completed = not task.completed
    task.save()
    return redirect('dashboard')

@login_required
def delete_task(request,id):
    Item.objects.get(pk=id).delete()
    return redirect('dashboard')

@login_required
def delete_filter(request,task_filter):
    if task_filter == "completed":
        Item.objects.filter(user=request.user,completed=True).delete()
    else:
        ids = [task.id for task in Item.objects.filter(user=request.user) if task.expired()]
        Item.objects.filter(id__in=ids).delete()
    return redirect('dashboard')

@login_required
def mail_list(request):
    tasks = [ task for task in Item.objects.filter(user=request.user) if not task.expired() and not task.completed ]
    sent = False

    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            task_list = "Hello {}, here are your tasks:\n\n".format(cd['email'])
            for idx,task in enumerate(tasks):
                task_list = task_list + "{}. {} is due on {}\nDescription: {}. This task has {} priority!\n\n".format(idx+1,task.title,task.date_due,task.description,task.priority)
            message = "Message from {} : {}".format(request.user,cd['comments'])
            subject = "Tasks sent by {}".format(request.user.email)
            message = task_list + message
            send_mail(subject,message,'djangouser123@gmail.com',(cd['email'],))
            sent = True
            messages.success(request,"Tasks sent successfully to {}".format(cd['email']))
    else:
        form = EmailForm()
    return render(request,'tasks/share.html',{'tasks':tasks,'form':form,'sent':sent})






    
        
    
    


