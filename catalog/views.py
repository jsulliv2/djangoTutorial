from django.contrib.auth.decorators import login_required # for functions
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin # for classes
from django.shortcuts import render
from django.views import generic

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

class allLoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    paginate_by = 20
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/all_loaned_books_list_view.html'

    def get_queryset(self):
        # import pdb; pdb.set_trace()
        return BookInstance.objects\
            .filter(status__exact='o')\
            .order_by('due_back', 'borrower', 'book')
