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
            
            sympthoms = [key.replace('_', ' ').title() for key, value in data["Inputs"]["input1"][0].items() if value == 1]
            results = clean_results(results)
            print(sympthoms)
            
            return render(request, "illness_result.html", {"data": results, "sympthoms": sympthoms})
    else:
        form = IllnessPredictorForm()
    
    return render(request, "illness_form.html", {"form": form})
