from django.contrib import admin
from .models import Author, Genre, Book, BookInstance, Language
# Register your models here.
# admin.site.register(Book)
# admin.site.register(Author)
admin.site.register(Genre)
# admin.site.register(BookInstance)
admin.site.register(Language)


class BookInline(admin.StackedInline):
    model = Book
    extra = 0


class AuthorAdmin(admin.ModelAdmin):
    # white list
    list_display = ('last_name', 'first_name',
                    'date_of_birth', 'date_of_death')
    # tuple leads to horizontal display, else vertical
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    # can also use exclude = to black list
    inlines = [BookInline]


admin.site.register(Author, AuthorAdmin)


# provides inline editing of associated records, StackedInline give vertical layout
class BooksInstanceInline(admin.TabularInline):
    model = BookInstance


# alternative way with declaration to create and assign ModelAdmin
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_filter = ('status', 'due_back')
    # provides sectioning in the detail view, None equals no section title
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )
    list_display = ['book', 'status', 'borrower', 'due_back', 'id']
    actions = ['markReturned', 'markMaint']

    @staticmethod
    def markReturned(request, queryset):
        queryset.update(status='a')

    @staticmethod
    def markMaint(request, queryset):
        queryset.update(status='m')
