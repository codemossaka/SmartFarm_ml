import pandas as pd
import numpy as np
import random


def generate_poultry_data(num_weeks=60, start_age=19, flock_id=1):
    data = []

    # Paramètres initiaux
    current_hens = 5000
    current_age = start_age

    for i in range(num_weeks):
        week_id = i + 1

        # 1. Simulation de la Température (Saisonnalité avec bruit)
        # Moyenne 22°C, varie entre 18 et 30
        avg_temp = 22 + 5 * np.sin(i / 8) + np.random.normal(0, 1.5)
        avg_temp = round(max(15, min(35, avg_temp)), 1)

        # 2. Simulation de la mortalité (augmente avec l'âge et la chaleur)
        base_mortality = 0.05 + (current_age * 0.002)  # Vieillissement
        heat_stress_factor = max(0, avg_temp - 27) * 0.05  # Chaleur > 27°C tue plus
        mortality_rate = round(base_mortality + heat_stress_factor + abs(np.random.normal(0, 0.02)), 2)

        # Mise à jour du nombre de poules
        dead_hens = int(current_hens * (mortality_rate / 100))
        current_hens -= dead_hens

        # 3. Courbe de ponte théorique (Modèle simplifié de Wood)
        # Montée rapide, pic vers 26-28 sem, déclin lent
        weeks_in_lay = current_age - 18
        if weeks_in_lay <= 0:
            theoretical_lay = 0
        else:
            # Formule approximative de courbe de ponte
            theoretical_lay = 0.97 * (1 - np.exp(-0.8 * weeks_in_lay)) * np.exp(-0.005 * weeks_in_lay)

        # Impact de la chaleur sur la ponte
        temp_penalty = max(0, avg_temp - 26) * 0.03

        # Disease outbreak (rare, 2% de chance)
        disease_outbreak = 1 if random.random() < 0.02 else 0
        disease_penalty = 0.30 if disease_outbreak else 0  # Grosse chute si maladie

        # Ponte réelle
        eggs_per_hen_day = theoretical_lay - temp_penalty - disease_penalty + np.random.normal(0, 0.01)
        eggs_per_hen_day = round(max(0, min(1, eggs_per_hen_day)), 3)

        # 4. Poids et Nourriture
        # Le poids monte jusqu'à sem 30 puis stagne
        weight_curve = 1.95 - 0.5 * np.exp(-0.15 * weeks_in_lay)
        avg_weight_kg = round(weight_curve + np.random.normal(0, 0.02), 2)

        # Feed intake suit la ponte + maintenance (poids)
        feed_need = (avg_weight_kg * 30) + (eggs_per_hen_day * 50)  # Formule simplifiée
        feed_g_per_hen_day = round(feed_need - (temp_penalty * 20), 1)  # Mange moins si chaud

        # 5. Autres variables
        feed_type = 1 if current_age < 23 else 2
        lights = 14 if current_age < 21 else 16

        # Calculs finaux
        total_eggs = int(current_hens * 7 * eggs_per_hen_day)

        # Classification
        # Seuil de performance : Si on est > 5% sous la courbe théorique
        is_low_perf = 1 if (theoretical_lay - eggs_per_hen_day) > 0.05 else 0

        if eggs_per_hen_day > 0.90:
            perf_class = 2  # High
        elif eggs_per_hen_day > 0.80:
            perf_class = 1  # Medium
        else:
            perf_class = 0  # Low

        data.append([
            week_id, flock_id, current_age, current_hens, feed_g_per_hen_day, feed_type,
            avg_temp, mortality_rate, avg_weight_kg, lights, disease_outbreak,
            eggs_per_hen_day, total_eggs, is_low_perf, perf_class
        ])

        current_age += 1

    columns = [
        "week_id", "flock_id", "age_weeks", "num_hens", "feed_g_per_hen_day",
        "feed_type", "avg_temp", "mortality_rate", "avg_weight_kg",
        "lights_hours_per_day", "disease_outbreak", "eggs_per_hen_day",
        "total_eggs_week", "is_low_performance", "performance_class"
    ]

    return pd.DataFrame(data, columns=columns)


df = generate_poultry_data()
print(df.head())
print("\nShape:", df.shape)

# Save to CSV
csv_filename = "eggs_farm_synthetic.csv"
df.to_csv(csv_filename, index=False)

# # Générer les données
# df = generate_poultry_data()
# print(df.head(10).to_csv(index=False))