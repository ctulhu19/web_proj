# Register your models here.
from django.contrib import admin
from .models import Category, Publication, Tags, Edition, Author

admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Publication)
admin.site.register(Tags)
admin.site.register(Edition)
