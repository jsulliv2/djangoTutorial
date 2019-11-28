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

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_authors': num_authors,
        'num_instances_available': num_instances_available,
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