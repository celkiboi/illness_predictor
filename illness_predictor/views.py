from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import IllnessPredictorForm, RegistrationForm
from .utils import predict, clean_results
from django.http import HttpResponseServerError
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, "home.html")

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect("illness_predictor")
    else:
        form = RegistrationForm()
    return render(request, "register.html", {"form": form})

def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("illness_predictor")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "login.html")

def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")

@login_required
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

            symptoms = [key.replace('_', ' ').replace('1','').title() for key, value in data["Inputs"]["input1"][0].items() if value == 1]
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
