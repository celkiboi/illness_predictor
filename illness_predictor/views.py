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
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import IllnessPrediction
from .serializers import IllnessPredictionSerializer
from .utils import predict, clean_results

def home(request):
    if not request.user.is_authenticated:
        return render(request, "home.html")
    else:
        return redirect("illness_predictor")
        

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


class GetPatientsBySymptoms(APIView):
    def get(self, request, *args, **kwargs):
        query_params = request.GET
        converted_params = {}

        for symptom, value in query_params.items():
            if value.lower() == "true":
                converted_params[symptom] = 1
            elif value.lower() == "false":
                converted_params[symptom] = 0
            else:
                return JsonResponse({"error": "Invalid value for symptom, expected true or false"}, status=400)

        all_patients = IllnessPrediction.objects.all()
        filtered_patients = []

        for patient in all_patients:
            match = True
            for symptom, value in converted_params.items():
                if symptom not in patient.symptoms or patient.symptoms[symptom] != value:
                    match = False
                    break

            if match:
                filtered_patients.append({
                    'username': patient.user.username if patient.user else None,
                    'email': patient.user.email if patient.user else None,
                    'prediction_id': patient.id
                })

        return Response({'patients': filtered_patients}, status=status.HTTP_200_OK)


class GetPatientsByDisease(APIView):
    def get(self, request, *args, **kwargs):
        diseases = request.GET.getlist('disease')
        if not diseases:
            return JsonResponse({"error": "Please enter at least one disease name"}, status=400)

        diseases = [disease.lower() for disease in diseases]
        all_patients = IllnessPrediction.objects.all()
        filtered_patients = []

        for patient in all_patients:
            predictions = patient.predictions
            if not predictions:
                continue

            highest_prediction = max(predictions, key=lambda x: x[1])

            if highest_prediction[0].lower() in diseases:
                filtered_patients.append({
                    'username': patient.user.username if patient.user else None,
                    'email': patient.user.email if patient.user else None,
                    'prediction_id': patient.id,
                    'highest_prediction': highest_prediction,
                })

        if not filtered_patients:
            return JsonResponse({"error": f"No patients with highest probability matching: {', '.join(diseases)}"}, status=404)

        return Response({'patients': filtered_patients}, status=status.HTTP_200_OK)


class GetSymptomsByDisease(APIView):
    def get(self, request, *args, **kwargs):
        diseases = request.GET.getlist('disease')

        if not diseases:
            return JsonResponse({"error": "Please enter at least one disease name"}, status=400)

        diseases = [d.lower() for d in diseases]
        all_patients = IllnessPrediction.objects.all()

        symptoms_data = None
        prediction_id = None

        for patient in all_patients:
            highest_prediction = max(patient.predictions, key=lambda x: x[1], default=None)

            if highest_prediction and highest_prediction[0].lower() in diseases:
                symptoms_data = patient.symptoms
                prediction_id = patient.id
                break

        if symptoms_data is None:
            return JsonResponse({"error": "No matching diseases found"}, status=404)

        return Response({
            "prediction_id": prediction_id,
            "symptoms": symptoms_data
        }, status=status.HTTP_200_OK)



class GetSymptomsByPredictionId(APIView):
    def get(self, request, *args, **kwargs):
        prediction_id = request.GET.get('id')
        try:
            prediction = IllnessPrediction.objects.get(id=prediction_id)
        except IllnessPrediction.DoesNotExist:
            return JsonResponse({"error": "Prediction ID not found"}, status=404)

        return Response({'symptoms': prediction.symptoms}, status=status.HTTP_200_OK)


class GetDiseasesBySymptoms(APIView):
    def get(self, request, *args, **kwargs):
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
                diseases_list.append({
                    "prediction_id": patient.id,
                    "diseases": patient.predictions
                })

        return Response({'diseases': diseases_list}, status=status.HTTP_200_OK)


class GetPredictionById(APIView):
    def get(self, request, prediction_id, *args, **kwargs):
        prediction = get_object_or_404(IllnessPrediction, id=prediction_id)
        sorted_results = sorted(prediction.predictions, key=lambda x: x[1], reverse=True)
        
        symptoms = prediction.symptoms

        return Response({
            "data": sorted_results,
            "symptoms": symptoms
        }, status=status.HTTP_200_OK)



class GetDiseasesByPredictionId(APIView):
    def get(self, request, *args, **kwargs):
        prediction_id = request.GET.get('id')
        try:
            prediction = IllnessPrediction.objects.get(id=prediction_id)
        except IllnessPrediction.DoesNotExist:
            return JsonResponse({"error": "Prediction ID not found"}, status=404)

        return Response({'diseases': [prediction.predictions]}, status=status.HTTP_200_OK)