from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from .models import Todo, Category
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, Submit
from crispy_forms.bootstrap import PrependedText
from django.contrib import messages

class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'description', 'due_date', 'priority', 'category', 'tags', 'progress']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select', 'required': False}),
            'progress': forms.NumberInput(attrs={'min': '0', 'max': '100', 'class': 'form-range'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
            self.fields['category'].required = False  # Make category optional
        
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div(Field('title'), css_class='col-md-12'),
                Div(Field('description'), css_class='col-md-12'),
                css_class='row mb-3'
            ),
            Div(
                Div(Field('due_date'), css_class='col-md-6'),
                Div(Field('priority'), css_class='col-md-6'),
                css_class='row mb-3'
            ),
            Div(
                Div(Field('category'), css_class='col-md-6'),
                Div(Field('tags'), css_class='col-md-6'),
                css_class='row mb-3'
            ),
            Div(
                Div(Field('progress'), css_class='col-md-12'),
                css_class='row'
            )
        )

class TodoListView(LoginRequiredMixin, ListView):
    model = Todo
    template_name = 'todoapp/todo_list.html'
    context_object_name = 'todos'

    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(user=self.request.user)
        return context

class TodoCreateView(LoginRequiredMixin, CreateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todoapp/todo_form.html'
    success_url = reverse_lazy('todoapp:todo_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            # Create default category if none exists
            if not Category.objects.filter(user=self.request.user).exists():
                Category.objects.create(
                    name='General',
                    color='#1a237e',
                    icon='fas fa-tasks',
                    user=self.request.user
                )
            context['categories'] = Category.objects.filter(user=self.request.user)
            return context
        except Exception as e:
            messages.error(self.request, f'Error loading form: {str(e)}')
            return {}

    def form_valid(self, form):
        try:
            # Set the user before saving
            form.instance.user = self.request.user
            
            # Save the form
            response = super().form_valid(form)
            
            # Add success message
            messages.success(self.request, f'Task "{form.instance.title}" created successfully!')
            
            # Print debug information
            print(f"Task created - Title: {form.instance.title}, User: {self.request.user.username}, ID: {form.instance.id}")
            
            return response
        except Exception as e:
            messages.error(self.request, f'Error creating task: {str(e)}')
            print(f"Error creating task: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'Error in {field}: {error}')
        return super().form_invalid(form)

class TodoUpdateView(LoginRequiredMixin, UpdateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todoapp/todo_form.html'
    success_url = reverse_lazy('todoapp:todo_list')

    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Task updated successfully!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class TodoDeleteView(LoginRequiredMixin, DeleteView):
    model = Todo
    template_name = 'todoapp/todo_confirm_delete.html'
    success_url = reverse_lazy('todoapp:todo_list')

    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Task deleted successfully!')
        return super().delete(request, *args, **kwargs)

class TodoCompleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        todo = Todo.objects.get(pk=pk, user=request.user)
        todo.completed = not todo.completed
        todo.save()
        messages.success(request, f'Task marked as {"completed" if todo.completed else "incomplete"}!')
        return redirect('todoapp:todo_list') 