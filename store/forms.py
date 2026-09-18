import ipaddress
from urllib.parse import urlparse
from django import forms
from .models import Order, Product, Category


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'notes']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Delivery Address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Order notes (optional)'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'sale_price', 'image', 'image_url', 'stock', 'is_active', 'is_featured']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and hasattr(image, 'size'):
            max_size = 5 * 1024 * 1024  # 5MB
            if image.size > max_size:
                raise forms.ValidationError("Product image cannot exceed 5MB.")
            valid_exts = ('.jpg', '.jpeg', '.png', '.webp')
            if not image.name.lower().endswith(valid_exts):
                raise forms.ValidationError("Only JPG, PNG, and WebP images are allowed.")
        return image

    def clean_image_url(self):
        url = self.cleaned_data.get('image_url')
        if url:
            parsed = urlparse(url)
            if parsed.scheme not in ('http', 'https'):
                raise forms.ValidationError("Image URL must use http or https.")
            hostname = parsed.hostname
            if not hostname:
                raise forms.ValidationError("Invalid image URL hostname.")

            # Prevent SSRF: block localhost and private network addresses
            if hostname.lower() in ('localhost', '127.0.0.1', '::1', '0.0.0.0'):
                raise forms.ValidationError("Local or private network image URLs are not permitted.")

            try:
                ip = ipaddress.ip_address(hostname)
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                    raise forms.ValidationError("Private network image URLs are not permitted.")
            except ValueError:
                # hostname is a domain name, not an IP address
                pass

        return url


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. fa-bag-shopping'}),
        }
