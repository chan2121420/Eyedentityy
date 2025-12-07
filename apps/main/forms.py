from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    image_url = forms.URLField(
        required=False,
        label="Image URL (optional)",
        help_text="Paste an image URL if you don't want to upload a file."
    )

    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'category', 'description', 'image', 'image_url',
            'price', 'old_price', 'lens_type', 'features', 'frame_material',
            'lens_material', 'stock_quantity', 'is_featured', 'is_on_sale', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'features': forms.CheckboxSelectMultiple,
        }

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        image_url = cleaned_data.get('image_url')
        if not image and not image_url:
            raise forms.ValidationError('Please provide an image file or an image URL.')
        return cleaned_data
