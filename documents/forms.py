from django import forms

from .models import Document


ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["file"]

    def clean_file(self):
        uploaded = self.cleaned_data["file"]

        if uploaded.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError(
                "Fichier trop volumineux (max 10 Mo)."
            )

        if uploaded.content_type not in ALLOWED_CONTENT_TYPES:
            raise forms.ValidationError(
                "Type de fichier non autorisé. Formats acceptés : PDF, JPG, PNG."
            )

        name_lower = uploaded.name.lower()
        if not any(name_lower.endswith(ext) for ext in ALLOWED_EXTENSIONS):
            raise forms.ValidationError(
                "Extension de fichier non autorisée."
            )

        return uploaded