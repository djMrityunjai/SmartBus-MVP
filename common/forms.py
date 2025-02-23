from django import forms
from django.utils import timezone

class BaseFormMixin(forms.ModelForm):
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Make timestamp and user fields read-only
        readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
        for field in readonly_fields:
            if field in self.fields:
                self.fields[field].widget.attrs['readonly'] = True
                self.fields[field].required = False

        # Hide system-managed fields from form
        hidden_fields = ['is_deleted']
        for field in hidden_fields:
            if field in self.fields:
                self.fields[field].widget = forms.HiddenInput()

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if self.user:
            if not instance.pk:  # New instance
                instance.created_by = self.user
            instance.updated_by = self.user

        if commit:
            instance.save()
        
        return instance

    # class Media:
    #     css = {
    #         'all': ('css/base_form.css',)
    #     }
    #     js = ('js/base_form.js',)

class AddressFormMixin(forms.ModelForm):
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add placeholders and classes for address fields
        address_fields = {
            'address': 'Enter full address',
            'city': 'Enter city',
            'state': 'Enter state',
            'zip_code': 'Enter ZIP code',
            'latitude': 'Latitude (optional)',
            'longitude': 'Longitude (optional)',
        }
        
        for field, placeholder in address_fields.items():
            if field in self.fields:
                self.fields[field].widget.attrs.update({
                    'placeholder': placeholder,
                    'class': 'address-field',
                })
                
                # Add specific classes for map fields
                if field in ['latitude', 'longitude']:
                    self.fields[field].widget.attrs['class'] += ' map-coordinate'

    def clean(self):
        cleaned_data = super().clean()
        
        # Validate coordinates if both are provided
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        
        if (latitude and not longitude) or (longitude and not latitude):
            raise forms.ValidationError(
                "Both latitude and longitude must be provided together."
            )
            
        if latitude and longitude:
            # Validate latitude range
            if not -90 <= float(latitude) <= 90:
                raise forms.ValidationError(
                    "Latitude must be between -90 and 90 degrees."
                )
            # Validate longitude range
            if not -180 <= float(longitude) <= 180:
                raise forms.ValidationError(
                    "Longitude must be between -180 and 180 degrees."
                )
        
        return cleaned_data

    # class Media:
    #     css = {
    #         'all': ('css/address_form.css',)
    #     }
    #     js = ('js/address_form.js', 'js/map_integration.js')