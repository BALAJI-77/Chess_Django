from django import forms
   
# creating a form 
class ProfileForm(forms.Form):
   
    first_name = forms.CharField(max_length = 200)
    last_name = forms.CharField(max_length = 200)
    short_desc = forms.CharField(max_length=100, help_text="Give your short description")
    long_desc = forms.CharField(widget=forms.Textarea())