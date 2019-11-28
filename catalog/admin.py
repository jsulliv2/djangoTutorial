from django.contrib import admin
from .models import Author, Genre, Book, BookInstance, Language
# Register your models here.
# admin.site.register(Book)
# admin.site.register(Author)
admin.site.register(Genre)
# admin.site.register(BookInstance)
admin.site.register(Language)

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name',
                    'date_of_birth', 'date_of_death')

admin.site.register(Author,AuthorAdmin)

# alternative way to create and assign ModelAdmin
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')

@admin.register(BookInstance)
class BookAdmin(admin.ModelAdmin):
    list_filter = ('status', 'due_back')

