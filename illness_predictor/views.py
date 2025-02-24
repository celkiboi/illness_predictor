from django.shortcuts import render
from .forms import IllnessPredictorForm
from .utils import predict, clean_results
from django.http import HttpResponseServerError

def illness_predictor_view(request):
    if request.method == "POST":
        form = IllnessPredictorForm(request.POST)
        if form.is_valid():
            data = {
                "Inputs": {
                    "input1": [
                        {key: int(value) for key, value in form.cleaned_data.items()}
                    ]
                }
            }

            results = predict(data)

            if results is None:
                return HttpResponseServerError("Something went wrong")

            symptoms = [key.replace('_', ' ').title() for key, value in data["Inputs"]["input1"][0].items() if value == 1]
            results = clean_results(results)

            sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)

            return render(request, "illness_result.html", {"data": sorted_results, "symptoms": symptoms})
    
    else:
        form = IllnessPredictorForm()

    symptom_categories = {
        "musculoskeletal": form.SYMPTOM_CATEGORIES["musculoskeletal"],
        "gastrointestinal": form.SYMPTOM_CATEGORIES["gastrointestinal"],
        "psychological": form.SYMPTOM_CATEGORIES["psychological"],
        "cardiovascular": form.SYMPTOM_CATEGORIES["cardiovascular"],
        "dermatological": form.SYMPTOM_CATEGORIES["dermatological"],
        "liver": form.SYMPTOM_CATEGORIES["liver_related"],
        "inflammatory": form.SYMPTOM_CATEGORIES["inflammatory"],
        "other": form.SYMPTOM_CATEGORIES["other"],
    }

    return render(request, "illness_form.html", {"form": form, **symptom_categories})
