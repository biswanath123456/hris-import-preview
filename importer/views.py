from django.shortcuts import render

from .services.import_service import process_import


def upload_csv(request):

    context = {
        "result": None,
    }

    if request.method == "POST":

        uploaded_file = request.FILES.get("file")

        if uploaded_file is None:

            context["error"] = "Please select a CSV file."

            return render(
                request,
                "importer/upload.html",
                context,
            )

        if not uploaded_file.name.lower().endswith(".csv"):

            context["error"] = "Only CSV files are supported."

            return render(
                request,
                "importer/upload.html",
                context,
            )

        result = process_import(uploaded_file)

        context["result"] = result

    return render(
        request,
        "importer/upload.html",
        context,
    )