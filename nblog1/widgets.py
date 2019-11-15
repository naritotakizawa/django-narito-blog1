from django import forms
from django.urls import reverse_lazy


class SuggestPostWidget(forms.SelectMultiple):
    template_name = 'nblog1/widgets/suggest.html'

    class Media:
        css = {
            'all': [
                'nblog1/css/admin_post_form.css',

            ]
        }
        js = ['nblog1/js/suggest.js']

    def __init__(self, attrs=None):
        super().__init__(attrs)
        if 'class' in self.attrs:
            self.attrs['class'] += ' suggest'
        else:
            self.attrs['class'] = 'suggest'


class UploadableTextarea(forms.Textarea):

    class Media:
        js = [
            'nblog1/js/csrf.js',
            'nblog1/js/upload.js'
        ]

    def __init__(self, attrs=None):
        super().__init__(attrs)
        if 'class' in self.attrs:
            self.attrs['class'] += ' uploadable vLargeTextField'
        else:
            self.attrs['class'] = 'uploadable vLargeTextField'
        self.attrs['data-url'] = reverse_lazy('nblog1:image_upload')


class CustomCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    template_name = 'nblog1/widgets/custom_checkbox.html'
    option_template_name = 'nblog1/widgets/custom_checkbox_option.html'

    def __init__(self, attrs=None):
        super().__init__(attrs)
        if 'class' in self.attrs:
            self.attrs['class'] += ' custom-checkbox'
        else:
            self.attrs['class'] = 'custom-checkbox'
