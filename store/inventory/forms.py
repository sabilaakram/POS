from django import forms
from .models import Products, Category
import unicodedata
import re
from django.core.exceptions import ValidationError

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        labels = {
            'name': 'Name',
            'description': 'Description',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter description', 'rows': 3}),
        }

class ProductsForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ['code', 'category', 'name', 'description', 'price', 'image']  # Removed cost, quantity, and status fields
        labels = {
            'code': 'Code',
            'category': 'Category',
            'name': 'Product Name',
            'description': 'Description',
            'price': 'Price',
            'image': 'Product Image',
        }
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product code'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter product description', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        error_messages = {
            'code': {
                'required': 'This field is required.',
                'max_length': 'This field cannot exceed 100 characters.',
            },
            'category': {
                'required': 'This field is required.',
            },
            'name': {
                'required': 'This field is required.',
            },
            'description': {
                'required': 'This field is required.',
            },
            'price': {
                'required': 'This field is required.',
                'invalid': 'Enter a valid price.',
            },
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name in self.errors:
                field.widget.attrs['class'] += ' is-invalid'
        
        # Sort the category queryset alphabetically
        self.fields['category'].queryset = Category.objects.all().order_by('name')

    @staticmethod
    def normalize_text(text):
        if text:
            # Remove accents and convert to lowercase
            text = ''.join(c for c in unicodedata.normalize('NFD', text)
                        if unicodedata.category(c) != 'Mn')
            # Remove special characters and spaces
            text = re.sub(r'[^\w]', '', text.lower())
        return text
    
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        code = cleaned_data.get('code')

        if name and code:
            normalized_name = self.normalize_text(name)
            normalized_code = self.normalize_text(code)

            # Get the current instance if we are editing
            instance_id = self.instance.pk if self.instance.pk else None

            # Check for name duplicates
            name_duplicates = Products.objects.all()
            if instance_id:
                name_duplicates = name_duplicates.exclude(pk=instance_id)
            
            for product in name_duplicates:
                if self.normalize_text(product.name) == normalized_name:
                    self.add_error('name', "A product with a similar name already exists.")
                    raise ValidationError("A product with a similar name already exists.")

            # Check for code duplicates
            code_duplicates = Products.objects.filter(code__iexact=normalized_code)
            if instance_id:
                code_duplicates = code_duplicates.exclude(pk=instance_id)
            if code_duplicates.exists():
                self.add_error('code', "A product with this code already exists.")
                raise ValidationError("A product with this code already exists.")

        return cleaned_data
