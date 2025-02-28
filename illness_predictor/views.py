from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import IllnessPredictorForm, RegistrationForm
from .utils import predict, clean_results
from django.http import JsonResponse
from django.db.models import Q
from django.http import HttpResponseServerError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from illness_predictor.models import IllnessPrediction

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
            predictions = sorted_results
            
            illness_prediction = IllnessPrediction(
                user = request.user,
                symptoms = {key: int(value) for key, value in form.cleaned_data.items()},
                predictions = predictions
            )
            illness_prediction.save()
            
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


def get_patients_by_symptoms(request):
    # Get all query parameters from the URL (the key-value pairs will represent symptom names and their values)
    query_params = request.GET

    # Map 'true' -> 1 and 'false' -> 0
    converted_params = {}
    for symptom, value in query_params.items():
        if value.lower() == "true":
            converted_params[symptom] = 1
        elif value.lower() == "false":
            converted_params[symptom] = 0
        else:
            # Return error if value isn't "true" or "false"
            return JsonResponse({"error": "Invalid value for symptom, expected true or false"}, status=400)

    # Get all IllnessPrediction entries
    all_patients = IllnessPrediction.objects.all()

    # Filter the patients in Python
    filtered_patients = []
    for patient in all_patients:
        match = True
        for symptom, value in converted_params.items():
            # Check if the symptom exists in the patient's data and if it matches the value
            if symptom not in patient.symptoms or patient.symptoms[symptom] != value:
                match = False
                break
        
        # If the patient matches all conditions, add to the result list
        if match:
            filtered_patients.append({
                'username': patient.user.username if patient.user else None,
                'email': patient.user.email if patient.user else None,
                'prediction_id': patient.id
            })

    # Return the response in JSON format
    return JsonResponse({'patients': filtered_patients})

def get_patients_by_disease(request):
    # Get 'disease' parameters from the URL query (support multiple diseases)
    diseases = request.GET.getlist('disease')

    if not diseases:
        return JsonResponse({"error": "Please enter at least one disease name"}, status=400)

    # Normalize disease names (convert to lowercase for case-insensitive comparison)
    diseases = [disease.lower() for disease in diseases]

    all_patients = IllnessPrediction.objects.all()

    filtered_patients = []

    for patient in all_patients:
        predictions = patient.predictions

        if not predictions:
            continue

        highest_prediction = max(predictions, key=lambda x: x[1])  # ('disease_name', probability)

        if highest_prediction[0].lower() in diseases:
            filtered_patients.append({
                'username': patient.user.username if patient.user else None,
                'email': patient.user.email if patient.user else None,
                'prediction_id': patient.id
            })

    if not filtered_patients:
        return JsonResponse({"error": f"No patients with highest probability matching: {', '.join(diseases)}"}, status=404)

    return JsonResponse({'patients': filtered_patients})

def get_symptoms_by_disease(request):
    diseases = request.GET.getlist('disease')

    if not diseases:
        return JsonResponse({"error": "Please enter at least one disease name"}, status=400)

    diseases = [d.lower() for d in diseases]
    all_patients = IllnessPrediction.objects.all()

    symptoms_data = {}

    for patient in all_patients:
        highest_prediction = max(patient.predictions, key=lambda x: x[1], default=None)

        if highest_prediction and highest_prediction[0].lower() in diseases:
            symptoms_data[patient.id] = patient.symptoms

    return JsonResponse({'symptoms': symptoms_data})


def get_symptoms_by_prediction_id(request):
    prediction_id = request.GET.get('id')

    try:
        prediction = IllnessPrediction.objects.get(id=prediction_id)
    except IllnessPrediction.DoesNotExist:
        return JsonResponse({"error": "Prediction ID not found"}, status=404)

    return JsonResponse({'symptoms': prediction.symptoms})


def get_diseases_by_symptoms(request):
    query_params = request.GET

    converted_params = {}
    for symptom, value in query_params.items():
        if not value:
            continue
        if value.lower() == "true":
            converted_params[symptom] = 1
        elif value.lower() == "false":
            converted_params[symptom] = 0
        else:
            return JsonResponse({"error": f"Invalid value for symptom '{symptom}', expected true or false"}, status=400)

    all_patients = IllnessPrediction.objects.all()
    diseases_list = []

    for patient in all_patients:
        match = all(patient.symptoms.get(symptom) == value for symptom, value in converted_params.items())

        if match:
            top_disease = max(patient.predictions, key=lambda x: x[1], default=None)
            if top_disease:
                diseases_list.append({
                    "prediction_id": patient.id,
                    "disease": top_disease[0]
                })

    return JsonResponse({'diseases': diseases_list})



@login_required
def get_prediction_by_id(request, prediction_id):
    prediction = get_object_or_404(IllnessPrediction, id=prediction_id)
    
    if request.user.id == prediction.user.id:
        print(request.user.username)
        # Make sure the variable 'req' is correctly defined
        print(request)
        
        sorted_results = sorted(prediction.predictions, key=lambda x: x[1], reverse=True)
        symptoms = [symptom for symptom, value in prediction.symptoms.items() if value == 1]

        return render(request, "illness_result.html", {"data": sorted_results, "symptoms": symptoms})
    else:
        return JsonResponse({"error": "Wrong ID"}, status=404)


def get_diseases_by_prediction_id(request):
    prediction_id = request.GET.get('id')
    try:
        prediction = IllnessPrediction.objects.get(id=prediction_id)
        top_disease = max(prediction.predictions, key=lambda x: x[1], default=None)
    except IllnessPrediction.DoesNotExist:
        return JsonResponse({"error": "Prediction ID not found"}, status=404)
    return JsonResponse({'disease': [top_disease]})