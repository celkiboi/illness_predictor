from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class IllnessPredictorForm(forms.Form):
    SYMPTOM_CATEGORIES = {
        "musculoskeletal": [
            ("muscle_pain", "Muscle pain"),
            ("swollen_extremeties", "Swollen extremities"),
            ("brittle_nails", "Brittle nails"),
            ("muscle_weakness", "Muscle weakness"),
            ("back_pain", "Back pain"),
            ("hip_joint_pain", "Hip joint pain"),
            ("knee_pain", "Knee pain"),
            ("cramps", "Cramps"),
            ("movement_stiffness", "Movement stiffness"),
            ("neck_pain", "Neck pain"),
            ("painful_walking", "Painful walking"),
        ],
        "gastrointestinal": [
            ("polyuria", "Polyuria"),
            ("increased_appetite", "Increased appetite"),
            ("stomach_bleeding", "Stomach bleeding"),
            ("blood_in_sputum", "Blood in sputum"),
            ("abnormal_menstruation", "Abnormal menstruation"),
            ("loss_of_appetite", "Loss of appetite"),
            ("excessive_hunger", "Excessive hunger"),
            ("pain_during_bowel_movements", "Pain during bowel movements"),
            ("pain_in_anal_region", "Pain in anal region"),
            ("irritation_in_anus", "Irritation in anus"),
            ("bloody_stool", "Bloody stool"),
            ("passage_of_gases", "Passage of gases"),
            ("belly_pain", "Belly pain"),
            ("constipation", "Constipation"),
            ("continuous_feel_of_urine", "Continuous feel of urine"),
            ("bladder_discomfort", "Bladder discomfort"),
            ("distention_of_abdomen", "Distention of abdomen"),
            ("yellow_urine", "Yellow urine"),
            ("weight_gain", "Weight gain"),
        ],
        "psychological": [
            ("coma", "Coma"),
            ("irritability", "Irritability"),
            ("slurred_speech", "Slurred speech"),
            ("depression", "Depression"),
            ("malaise", "Malaise"),
            ("anxiety", "Anxiety"),
            ("lack_of_concentration", "Lack of concentration"),
            ("mood_swings", "Mood swings"),
            ("restlessness", "Restlessness"),
            ("altered_sensorium", "Altered sensorium"),
        ],
        "cardiovascular": [
            ("palpitations", "Palpitations"),
            ("fast_heart_rate", "Fast heart rate"),
            ("chest_pain", "Chest pain"),
            ("prominent_veins_on_calf", "Prominent veins on calf"),
            ("cold_hands_and_feets", "Cold hands and feet"),
            ("irregular_sugar_level", "Irregular sugar level"),
            ("fluid_overload_1", "Fluid overload"),
        ],
        "dermatological": [
            ("redness_of_eyes", "Redness of eyes"),
            ("loss_of_smell", "Loss of smell"),
            ("red_spots_over_body", "Red spots over body"),
            ("drying_and_tingling_lips", "Drying and tingling lips"),
            ("puffy_face_and_eyes", "Puffy face and eyes"),
            ("swollen_legs", "Swollen legs"),
            ("inflammatory_nails", "Inflammatory nails"),
            ("small_dents_in_nails", "Small dents in nails"),
            ("silver_like_dusting", "Silver-like dusting"),
            ("blister", "Blister"),
            ("yellow_crust_ooze", "Yellow crust ooze"),
        ],
        "liver_related": [
            ("yellowing_of_eyes", "Yellowing of eyes"),
            ("acute_liver_failure", "Acute liver failure"),
            ("history_of_alcohol_consumption", "History of alcohol consumption"),
        ],
        "inflammatory": [
            ("pain_behind_the_eyes", "Pain behind the eyes"),
            ("sinus_pressure", "Sinus pressure"),
            ("throat_irritation", "Throat irritation"),
            ("runny_nose", "Runny nose"),
            ("congestion", "Congestion"),
            ("mild_fever", "Mild fever"),
            ("phlegm", "Phlegm"),
            ("rusty_sputum", "Rusty sputum"),
            ("swelled_lymph_nodes", "Swelled lymph nodes"),
            ("mucoid_sputum", "Mucoid sputum"),
            ("toxic_look_(typhos)", "Toxic look (typhos)"),
            ("internal_itching", "Internal itching"),
        ],
        "other": [
            ("receiving_blood_transfusion", "Receiving blood transfusion"),
            ("receiving_unsterile_injections", "Receiving unsterile injections"),
            ("enlarged_thyroid", "Enlarged thyroid"),
            ("visual_disturbances", "Visual disturbances"),
            ("unsteadiness", "Unsteadiness"),
            ("bruising", "Bruising"),
            ("swelling_of_stomach", "Swelling of stomach"),
        ],
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for category, symptoms in self.SYMPTOM_CATEGORIES.items():
            for symptom, label in symptoms:
                self.fields[symptom] = forms.BooleanField(
                    required=False, label=label, widget=forms.CheckboxInput()
                )

    def clean(self):
        cleaned_data = super().clean()
        selected_symptoms = sum(
            1 for category, symptoms in self.SYMPTOM_CATEGORIES.items()
            for symptom, _ in symptoms if cleaned_data.get(symptom, False)
        )
        if selected_symptoms < 3:
            raise forms.ValidationError('Please select at least 3 symptoms.')
        return cleaned_data

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]