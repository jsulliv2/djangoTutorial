from datetime import date, timedelta


from django.contrib.auth.decorators import login_required, permission_required  # for functions
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin  # for classes
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy

from catalog.forms import RenewBookForm, RenewBookModelForm
from catalog.models import Book, Author, BookInstance, Genre

# Create your views here.


def index(request):
    """
        View function for home page of site
        @param request      : request object
        @return             : index template with context data
    """

    # Generate counts of some of the main objects, all() implied by default
    num_books = Book.objects.count()
    num_instances = BookInstance.objects.count()
    num_authors = Author.objects.count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # Number of visits to this view, as counted by session
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_authors': num_authors,
        'num_instances_available': num_instances_available,
        'num_visits': num_visits,
    }

    # always include the original request object
    return render(request, 'index.html', context=context)


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)
    if request.method == 'POST':
        form = RenewBookModelForm(request.POST)
        if form.is_valid():
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()
            return HttpResponseRedirect(reverse('all-borrowed'))
    else:
        proposed_renewal_date = date.today() + timedelta(weeks=3)
        form = RenewBookModelForm(initial={'due_back': proposed_renewal_date})
    context = {
        'form': form,
        'book_instance': book_instance
    }
    return render(request, 'catalog/book_renew_librarian.html', context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

    def get_queryset(self):
        return Book.objects.order_by('author', 'title')


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

    # no get_queryset, order set on model level


class AuthorDetailView(generic.DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user"""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects\
                           .filter(borrower=self.request.user)\
                           .filter(status__exact='o')\
                           .order_by('due_back')


class AllLoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    paginate_by = 20
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/all_loaned_books_list_view.html'

    def get_queryset(self):
        return BookInstance.objects\
            .filter(status__exact='o')\
            .order_by('due_back', 'borrower', 'book')


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    permission_required = 'catalog.can_mark_returned'
    fields = '__all__'
    # just an example on how to set initial: initial = {'date_of_death': '05/01/2018'}


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    permission_required = 'catalog.can_mark_returned'
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    permission_required = 'catalog.can_mark_returned'
    success_url = reverse_lazy('authors')
    template_name_suffix = '_delete'


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    permission_required = 'catalog.can_mark_returned'
    fields = '__all__'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    permission_required = 'catalog.can_mark_returned'
    fields = '__all__'


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    permission_required = 'catalog.can_mark_returned'
    success_url = reverse_lazy('books')
    template_name_suffix = '_delete'

