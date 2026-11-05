import os
import zipfile
from django import forms

MAX_CV_SIZE = 5 * 1024 * 1024
ALLOWED_EXT = {".pdf", ".doc", ".docx"}


class ContactForm(forms.Form):
    name = forms.CharField(max_length=120)
    email = forms.EmailField(max_length=180)
    message = forms.CharField(max_length=1500)
    website_url = forms.CharField(required=False, max_length=200)  # honeypot


class CVForm(forms.Form):
    name = forms.CharField(max_length=120)
    email = forms.EmailField(max_length=180)
    phone = forms.CharField(max_length=30)
    field = forms.CharField(required=False, max_length=120)
    message = forms.CharField(required=False, max_length=1500)
    cv = forms.FileField()
    website_url = forms.CharField(required=False, max_length=200)  # honeypot

    def clean_cv(self):
        f = self.cleaned_data["cv"]
        if f.size > MAX_CV_SIZE:
            raise forms.ValidationError("File too large (max 5MB).")
        if os.path.splitext(f.name)[1].lower() not in ALLOWED_EXT:
            raise forms.ValidationError("Only PDF or Word files are accepted.")
        ext = os.path.splitext(f.name)[1].lower()
        head = f.read(8); f.seek(0)
        if ext == ".pdf":
            good = head.startswith(b"%PDF-")
        elif ext == ".doc":
            good = head.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1")
        else:  # .docx = a zip that contains word/document.xml
            try:
                with zipfile.ZipFile(f) as z:
                    good = "word/document.xml" in z.namelist() and sum(i.file_size for i in z.infolist()) < 200 * 1024 * 1024
            except zipfile.BadZipFile:
                good = False
            f.seek(0)
        if not good:
            raise forms.ValidationError("The file content does not match a real PDF/Word document.")
        return f