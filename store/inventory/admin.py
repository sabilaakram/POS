from django.contrib import admin
from .models import Category, Products

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'date_added', 'date_updated')  # Removed 'status'
    search_fields = ('name', 'description')
    list_filter = ('date_added', 'date_updated')  # Removed 'status' from filters

class ProductsAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'category', 'price', 'date_added', 'date_updated')  # Removed 'status', 'quantity'
    search_fields = ('code', 'name', 'description')
    list_filter = ('category', 'date_added', 'date_updated')  # Removed 'status'

    # Add the image field if you want it to appear in the list_display
    # If you want the image field to be shown in the admin interface but not in the table listing, you can remove it from here.

admin.site.register(Category, CategoryAdmin)
admin.site.register(Products, ProductsAdmin)
