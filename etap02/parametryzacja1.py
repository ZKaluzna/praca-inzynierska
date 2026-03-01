import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from scipy.optimize import differential_evolution
from model import PopulationModel, Individual, Predator
import time
import sys
import os
import tempfile
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

# =================================================================
# 1. USTAWIENIA CZASU I DOKŁADNOŚCI
# =================================================================
SIM_STEPS = 250          
BURN_IN_STEPS = 150      
N_RUNS_PER_EVAL = 12    
DE_MAXITER = 30          
DE_POPSIZE = 10          
WORKERS = 4    

# --- KONFIGURACJA PLIKÓW ---
DATA_FILE = "Spot_area_and_number.csv"
CONFIG_FILE = "config.json"
TARGET_POPULATION = "Aripo1"

# --- ZAKRESY POSZUKIWAŃ PARAMETRÓW (14 PARAMETRÓW) ---
PARAM_BOUNDS = {
# --- ZAKRESY POSZUKIWAŃ PARAMETRÓW (ZBALANSOWANE) ---
PARAM_BOUNDS = {
    "reproduction_prob":          (0.25, 0.8),    # Podniesione minimum (musi być regeneracja populacji)
    "env_death_prob":             (0.005, 0.04),  # Zwężone (zbyt duża losowa śmierć niszczy model)
    "max_age":                    (50.0, 150.0),  # Podniesione minimum (krótsze życie to zbyt duży szum)
    "guppy_start_energy":         (20.0, 50.0),   # Większy zapas na start (szansa na znalezienie 1. jedzenia)
    "guppy_energy_decay":         (1.0, 5.0),     # Drastycznie obniżone max (nie mogą spalać się w 1 turę)
    "guppy_energy_gain_per_food": (4.0, 12.0),    # Podniesione (jedzenie musi dawać wymierną korzyść)
    
    # Drapieżniki (4)
    "predator_hunt_threshold":    (10.0, 40.0),   # Bardziej stabilne progi polowania
    "predator_energy_decay":      (0.5, 3.0),     # Obniżone (drapieżnik nie może znikać natychmiast)
    "predator_energy_gain":       (5.0, 15.0),    # Zbalansowane pod kątem energii gupika
    "predator_start_energy":      (20.0, 40.0),   
    
    # Środowisko (4)
    "food_max":                   (15.0, 60.0),   # Zwiększone minimum (musi być co jeść)
    "food_regen":                 (2.0, 15.0),    # Zwiększone (szybsze odnawianie zasobów)
    "food_eat":                   (8.0, 20.0),    # Większy kęs = szybsza regeneracja gupika
    "food_regen_empty_multiplier": (1.2, 3.5), 
}

pbar = None

# =================================================================
# 2. LOGIKA OBLICZENIOWA
# =================================================================

def load_base_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"BŁĄD: Nie można wczytać {CONFIG_FILE}: {e}")
        sys.exit(1)

BASE_PARAMS = load_base_config()

def run_single_simulation(optimized_params_dict, seed=None):
    """Pojedynczy bieg modelu z użyciem tymczasowego pliku JSON."""
    full_params = {**BASE_PARAMS, **optimized_params_dict}
    if seed is not None:
        full_params["seed"] = seed
        
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        json.dump(full_params, tmp)
        tmp_path = tmp.name

    try:
        model = PopulationModel(config_path=tmp_path)
        collected_data = []
        for i in range(SIM_STEPS):
            model.step()
            if i >= BURN_IN_STEPS:
                # ZBIERAMY N_black (zgodnie z Twoją prośbą)
                males_black = [a.N_black for a in model.agents if isinstance(a, Individual) and a.sex == "M"]
                collected_data.extend(males_black)
            if not model.agents: break
        return collected_data
    except Exception:
        return []
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def run_simulation_batch(params_dict, n_runs):
    all_values = []
    seeds = [np.random.randint(0, 100000) for _ in range(n_runs)]
    
    if n_runs > 1 and WORKERS > 1:
        with ProcessPoolExecutor(max_workers=WORKERS) as executor:
            futures = [executor.submit(run_single_simulation, params_dict, s) for s in seeds]
            for f in futures:
                all_values.extend(f.result())
    else:
        for s in seeds:
            all_values.extend(run_single_simulation(params_dict, s))
    return all_values

def negative_log_likelihood(params_vec, param_names, real_data):
    global pbar
    params_dict = dict(zip(param_names, params_vec))
    sim_data = run_simulation_batch(params_dict, n_runs=N_RUNS_PER_EVAL)
    
    if len(sim_data) < 20: 
        if pbar: pbar.update(1)
        return 1e6 + (1000 * (20 - len(sim_data))) 
    
    max_val = int(max(np.max(real_data), np.max(sim_data), 15))
    bins = np.arange(0, max_val + 2) - 0.5
    real_counts, _ = np.histogram(real_data, bins=bins)
    sim_counts, _ = np.histogram(sim_data, bins=bins)
    
    k_categories = len(bins) - 1
    sim_probs = (sim_counts + 1) / (np.sum(sim_counts) + k_categories)
    nll = -np.sum(real_counts * np.log(sim_probs))
    
    if pbar:
        pbar.update(1)
        pbar.set_postfix({"NLL": f"{nll:.2f}", "Pop": len(sim_data)})
        
    return nll

# =================================================================
# 3. URUCHOMIENIE
# =================================================================

if __name__ == "__main__":
    try:
        df = pd.read_csv(DATA_FILE)
        # UWAGA: Zmieniono 'orange_N' na 'black_N'. Sprawdź czy tak nazywa się kolumna w CSV!
        real_data = df[df["pop"] == TARGET_POPULATION]["black_N"].values
        if len(real_data) == 0:
            raise ValueError(f"Brak danych dla populacji {TARGET_POPULATION} w kolumnie 'black_N'")
    except Exception as e:
        print(f"BŁĄD DANYCH: {e}")
        sys.exit(1)
    
    param_names = list(PARAM_BOUNDS.keys())
    bounds = [PARAM_BOUNDS[name] for name in param_names]
    
    total_evals = (DE_MAXITER + 1) * DE_POPSIZE * len(param_names)
    
    print(f"Optymalizacja MLE (CZARNE PLAMKI) dla: {TARGET_POPULATION}")
    print(f"Przewidywana liczba symulacji: {total_evals * N_RUNS_PER_EVAL}")
    
    start_time = time.time()
    pbar = tqdm(total=total_evals, desc="Postęp optymalizacji", unit="eval")
    
    try:
        result = differential_evolution(
            negative_log_likelihood,
            bounds=bounds,
            args=(param_names, real_data),
            maxiter=DE_MAXITER,
            popsize=DE_POPSIZE,
            workers=1
        )
    finally:
        pbar.close()
    
    duration = (time.time() - start_time) / 60
    best_params = dict(zip(param_names, result.x))
    
    print("Generowanie wyników końcowych dla czarnych plamek...")
    final_sim_data = run_simulation_batch(best_params, n_runs=50) 

    plt.figure(figsize=(10, 6))
    viz_bins = np.arange(0, 18) - 0.5 
    plt.hist(real_data, bins=viz_bins, density=True, color='#b3b3b3', edgecolor='#666666', label='Dane Rzeczywiste (Black)')
    if final_sim_data:
        plt.hist(final_sim_data, bins=viz_bins, density=True, color='black', histtype='step', linewidth=2, label='Zoptymalizowany Model')

    plt.title(f"Wynik MLE (Czarne plamki): {TARGET_POPULATION}\nNLL: {result.fun:.2f}")
    plt.xlabel("Liczba czarnych plamek (black_N)")
    plt.ylabel("Gęstość")
    plt.legend()
    plt.savefig("wykres_mle_black_14p.png")
    
    with open("wyniki_parametry_black_14p.txt", "w") as f:
        f.write(f"ZOPTYMALIZOWANE PARAMETRY (BLACK SPOTS) DLA {TARGET_POPULATION}:\n")
        f.write(f"NAJLEPSZY NLL: {result.fun:.4f}\n")
        for k, v in best_params.items():
            f.write(f"{k}: {v:.6f}\n")
    
    print(f"Zakończono w {duration:.1f} min. Wyniki zapisano.")
    plt.show()