from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'todoapp'

urlpatterns = [
    path('', login_required(views.TodoListView.as_view()), name='todo_list'),
    path('create/', login_required(views.TodoCreateView.as_view()), name='todo_create'),
    path('update/<int:pk>/', login_required(views.TodoUpdateView.as_view()), name='todo_update'),
    path('delete/<int:pk>/', login_required(views.TodoDeleteView.as_view()), name='todo_delete'),
    path('complete/<int:pk>/', login_required(views.TodoCompleteView.as_view()), name='todo_complete'),
] 