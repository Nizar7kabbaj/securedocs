from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DocumentUploadForm
from .models import Document
from .services import classify_document


@login_required
def upload(request):
    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.owner = request.user
            document.original_name = request.FILES["file"].name
            document.save()

            try:
                text, label, confidence = classify_document(document.file.path)
                document.extracted_text = text
                document.classification = label
                document.confidence = confidence
                document.save(update_fields=[
                    "extracted_text",
                    "classification",
                    "confidence",
                ])
                messages.success(
                    request,
                    f"Document téléversé et classé comme « {label} » "
                    f"({confidence:.0%} de confiance).",
                )
            except Exception:
                messages.warning(
                    request,
                    "Document téléversé, mais l'extraction ou la classification a échoué.",
                )

            return redirect("documents:list")
    else:
        form = DocumentUploadForm()

    return render(request, "documents/upload.html", {"form": form})


@login_required
def document_list(request):
    documents = request.user.documents.order_by("-uploaded_at")
    return render(request, "documents/list.html", {"documents": documents})


@login_required
def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk, owner=request.user)
    return render(request, "documents/detail.html", {"document": document})


@login_required
def document_download(request, pk):
    document = get_object_or_404(Document, pk=pk, owner=request.user)
    return FileResponse(
        document.file.open("rb"),
        as_attachment=True,
        filename=document.original_name,
    )