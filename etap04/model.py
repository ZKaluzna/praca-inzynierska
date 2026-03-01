import mesa
import json
from pathlib import Path


class Individual(mesa.Agent):
    def __init__(self, model, sex):
        super().__init__(model)
        self.sex = sex          # M/F
        self.age = 0
        self.alive = True   #zywy/martwy
        self.energy = self.model.guppy_start_energy

        if self.sex == "M":
            self.N_orange = self.model.random.randint(0, 5)
            self.N_black = self.model.random.randint(0, 5)
            self.body_size = self.model.random.uniform(1.5,4)
            self.orange_area = self.model.random.uniform(0,0.5) #procent pokrycia
            self.black_area = self.model.random.uniform(0,0.5)  #procent pokrycia

        if self.sex == "F":
            self.preference_orange = self.model.female_pref_orange
            self.preference_black = self.model.female_pref_black
            self.preference_body_size = self.model.female_pref_body_size
            self.preference_N_orange = self.model.female_pref_N_orange
            self.preference_N_black = self.model.female_pref_N_black

    def score_males(self, male): # taka sama bedzie dla samic i predatorow 
        N_orange = male.N_orange 
        N_black = male.N_black 
        body_size = male.body_size 
        orange_area= male.orange_area 
        black_area = male.black_area 

        score = 0
        score += (N_orange/5) * self.preference_N_orange
        score += (N_black/5) * self.preference_N_black 
        score += (body_size/4) *self.preference_body_size
        score += (orange_area*2) * self.preference_orange 
        score += (black_area*2) * self.preference_black
        
        if score > 5:
            print("\nscore liczy za duzo w males")
        
# czy to skaluje sie do zakresu od 0 do 5, jezzeli jest inna wartosc to jest blad w kodzie / przy drapuezniku tez 
        return score

    def step(self):
        if not self.alive:
            return

        # koszt kroku symulacji/zycia
        self.energy -= self.model.guppy_energy_decay
        #patrzy jakie jest sasiedztwo dookolo niego
        neighborhood = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False,) 
        empty_neighbors = [pos for pos in neighborhood if self.model.grid.is_cell_empty(pos)]

        if empty_neighbors:
            # znajduje kratke z makstmalnym jedzeniem wsrod pustych sasiadow
            best_food = max(self.model.food[y][x] for (x, y) in empty_neighbors)
            best_positions = [(x, y) for (x, y) in empty_neighbors if self.model.food[y][x] == best_food] #wybiera losowa kratke wsrod maksymalnych
            new_position = self.model.random.choice(best_positions)
            self.model.grid.move_agent(self, new_position)

       #tu jedzenie z kratek 
        x, y = self.pos #aktualna pozycja gupika 
        available = self.model.food[y][x] #sprawdza ile jest jedzenia na kratce 
        eat = min(available, self.model.food_eat) #limit jedzenia na krok, bo nie moze zjesc mniej niz jest 
        self.model.food[y][x] -= eat #zjedzenie jedzenia z kratki
        self.energy += eat * self.model.guppy_energy_gain_per_food #energia z jedzebnia

        self.age += 1
        self.check_death()

    def check_death(self):
        if self.energy <= 0: #umiera z bralu energii
            self.alive = False
            return

        if self.model.random.random() < self.model.env_death_prob: #smierc losowa srodowiskowa
            self.alive = False
            return

        if self.age > self.model.max_age: #smierc ze starosci
            self.alive = False
            return


class Predator(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.alive = True
        self.energy = self.model.predator_start_energy

        self.predator_preference_orange = self.model.pred_pref_orange
        self.predator_preference_black = self.model.pred_pref_black
        self.predator_preference_body_size = self.model.pred_pref_body_size
        self.predator_preference_N_orange = self.model.pred_pref_N_orange
        self.predator_preference_N_black = self.model.pred_pref_N_black

    def score_males(self, male): # taka sama bedzie dla samic i predatorow 
               
        N_orange = male.N_orange 
        N_black = male.N_black 
        body_size = male.body_size 
        orange_area= male.orange_area 
        black_area = male.black_area 

        score = 0
        score += (N_orange/5) * self.predator_preference_N_orange
        score += (N_black/5) * self.predator_preference_N_black 
        score += (body_size/4) *self.predator_preference_body_size
        score += (orange_area*2) * self.predator_preference_orange 
        score += (black_area*2) * self.predator_preference_black

        if score > 5:
            print("\nscore liczy za duzo w males w drapiezniku")

        return score

    def step(self):
        if not self.alive:
            return

        # koszt życia
        self.energy -= self.model.predator_energy_decay

        if self.energy <= 0:  #moze umrzec tylko z brau energii/glodu
            self.alive = False
            return

        #może wejść na pustą kratkę ALBO na kratkę z gupikiem
        neighborhood = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)

        candidates = [] #to sa kratki na ktore moze wejsc predator, czyli albo puste kratki albo kratki z gupikiem
        #zeby nie wejsc na drugiego predatora
        for pos in neighborhood:
            cell_agents = self.model.grid.get_cell_list_contents([pos])

            # pusta kratka
            if not cell_agents:
                candidates.append(pos)
                continue

            # kratka z gupikiem 
            if any(isinstance(a, Individual) for a in cell_agents):
                candidates.append(pos)

        if candidates:
            self.model.grid.move_agent(self, self.model.random.choice(candidates))

        # polowanie tylko gdy głodny
        if self.energy <= self.model.predator_hunt_threshold:
            self.hunt()

    def hunt(self): #niech zjada tez samice
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=True)
        males = [a for a in neighbors if isinstance(a, Individual) and a.sex == "M" and a.alive] #ofiary to tylko samce
        females = [a for a in neighbors if isinstance(a, Individual) and a.sex == "F" and a.alive]

        if ((not males) and (not females)):
            return

        #losowa samica lub wybrany samiec
        x = self.model.random.random() #zmienna x z zakresu 0 1 # to bedzie random uniform to rozklad jednorodny jezeli wybierze samice to koniec jakis return czy cos else
        if x <= 0.1 and females:
            victim = self.model.random.choice(females)
        else: 
            if not males:
                return

            victim = males[0]
            for male in males:
                score_tmp = self.score_males(male)
                score_victim = self.score_males(victim)
                if score_tmp > score_victim:
                    victim = male

        victim.alive = False
        if victim.sex == "M":
            self.energy += self.model.predator_energy_gain * (victim.body_size / 4) #bo body zise maksymalny jest 4, natomiast jezeli samica to moze byc *1 bez zmian 
        else:
            self.energy += self.model.predator_energy_gain


class PopulationModel(mesa.Model):
    def __init__(self, config_path=None, **kwargs):
    #tu zabezpieczenia 
        if kwargs:
            bad = ", ".join(sorted(kwargs.keys()))
            raise TypeError(
                f"PopulationModel nie przyjmuje parametrów w kodzie. "
                f"Wszystko ustaw w config.json. Nieobsługiwane: {bad}"
            )

        default_path = Path(__file__).with_name("config.json")
        path = Path(config_path) if config_path is not None else default_path

        if not path.exists():
            raise FileNotFoundError(
                f"Brak pliku config.json: {path}\n"
                f"Utwórz config.json obok model.py albo podaj config_path."
            )

        with path.open("r", encoding="utf-8") as f:
            cfg = json.load(f)

        if not isinstance(cfg, dict):
            raise ValueError("config.json musi zawierać obiekt JSON (słownik).")

        # Wczytanie wartości z configu
        n_agents = int(cfg["n_agents"])
        width = int(cfg["width"])
        height = int(cfg["height"])
        reproduction_prob = float(cfg["reproduction_prob"])
        env_death_prob = float(cfg["env_death_prob"])
        max_age = int(cfg["max_age"])
        # seed = int(cfg["seed"])
        seed = None

        n_predators = int(cfg["n_predators"])
        predator_start_energy = float(cfg["predator_start_energy"])
        predator_energy_decay = float(cfg["predator_energy_decay"])
        predator_hunt_threshold = float(cfg["predator_hunt_threshold"])
        predator_energy_gain = float(cfg["predator_energy_gain"])

        food_max = float(cfg["food_max"])
        food_regen = float(cfg["food_regen"])
        food_eat = float(cfg["food_eat"])
        food_regen_empty_multiplier = float(cfg["food_regen_empty_multiplier"])

        guppy_start_energy = float(cfg["guppy_start_energy"])
        guppy_energy_decay = float(cfg["guppy_energy_decay"])
        guppy_energy_gain_per_food = float(cfg["guppy_energy_gain_per_food"])

        self.female_pref_orange = float(cfg["female_pref_orange"])
        self.female_pref_black = float(cfg["female_pref_black"])
        self.female_pref_body_size = float(cfg["female_pref_body_size"])
        self.female_pref_N_orange = float(cfg["female_pref_N_orange"])
        self.female_pref_N_black = float(cfg["female_pref_N_black"])

        self.pred_pref_orange = float(cfg["pred_pref_orange"])
        self.pred_pref_black = float(cfg["pred_pref_black"])
        self.pred_pref_body_size = float(cfg["pred_pref_body_size"])
        self.pred_pref_N_orange = float(cfg["pred_pref_N_orange"])
        self.pred_pref_N_black = float(cfg["pred_pref_N_black"])

        super().__init__(seed=seed)

        # Bezpiecznik przed zawieszeniem na losowaniu wolnych kratek
        if n_agents + n_predators > width * height:
            raise ValueError(
                f"Za dużo agentów na siatkę: n_agents({n_agents}) + n_predators({n_predators}) > width*height({width*height})"
            )

       #ladowanie parametrów
        self.params = dict(cfg)
        self.params["config_path"] = str(path)

        self.reproduction_prob = reproduction_prob
        self.env_death_prob = env_death_prob
        self.max_age = max_age

        self.n_predators = n_predators
        self.predator_start_energy = predator_start_energy
        self.predator_energy_decay = predator_energy_decay
        self.predator_hunt_threshold = predator_hunt_threshold
        self.predator_energy_gain = predator_energy_gain

        self.food_max = food_max
        self.food_regen = food_regen
        self.food_eat = food_eat
        self.food_regen_empty_multiplier = food_regen_empty_multiplier

        self.guppy_start_energy = guppy_start_energy
        self.guppy_energy_decay = guppy_energy_decay
        self.guppy_energy_gain_per_food = guppy_energy_gain_per_food

        self.step_count = 0
        self.births_last_step = 0
        self.deaths_last_step = 0
        self.predator_deaths_last_step = 0


        self.running = True
        self.grid = mesa.space.MultiGrid(width, height, torus=True)

        # macierz jedzenia[y][x]
        self.food = [[self.food_max for _ in range(width)] for _ in range(height)]

        # tworzenie gupikow startowych
        for _ in range(n_agents):
            sex = self.random.choice(["M", "F"])
            agent = Individual(self, sex)
            while True:
                x = self.random.randrange(width)
                y = self.random.randrange(height)
                if self.grid.is_cell_empty((x, y)): #losowanie pozycji
                    self.grid.place_agent(agent, (x, y))
                    break

        # tworzenie drapieżnikow podobnie jak gupiki 
        for _ in range(n_predators):
            predator = Predator(self)
            while True:
                x = self.random.randrange(width)
                y = self.random.randrange(height)
                if self.grid.is_cell_empty((x, y)):
                    self.grid.place_agent(predator, (x, y))
                    break

    def regenerate_food(self):
        for y in range(self.grid.height):
            for x in range(self.grid.width): #iterowanie po kazdej kratce
                # cell_agents = self.grid.get_cell_list_contents([(x, y)])
                    #has_guppy = any(isinstance(a, Individual) for a in cell_agents) #jezeli na kratce nie ma gupika to regeneruje sie szybciej
                    #regen = self.food_regen if has_guppy else (self.food_regen_empty_multiplier * self.food_regen)
                regen = self.food_regen_empty_multiplier * self.food_regen
                self.food[y][x] = min(self.food_max, self.food[y][x] +regen) #nie przekracza maksymalnej pojemnosci jedzenia na kratce

    def step(self):
        self.step_count += 1
        self.births_last_step = 0
        self.deaths_last_step = 0  # zerowanie statystyk ostatniego kroku
        self.predator_deaths_last_step = 0


        self.regenerate_food()
        self.agents.shuffle_do("step")  # wszyscy wykonują ruch w losowej kolejności

        dead_predators = 0

        # usuwanie martwych
        for agent in list(self.agents):
            if isinstance(agent, (Individual, Predator)) and not agent.alive:
                self.grid.remove_agent(agent)
                self.agents.remove(agent)

                if isinstance(agent, Individual):
                    self.deaths_last_step += 1
                elif isinstance(agent, Predator):
                    dead_predators += 1
                    self.predator_deaths_last_step += 1

        # respawn drapieżników 
        for _ in range(dead_predators):
            predator = Predator(self)

            placed = False
            
            for _try in range(self.grid.width * self.grid.height):
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
                pos = (x, y)

                cell_agents = self.grid.get_cell_list_contents([pos])

                # nie staje na kratce z innym predatorem
                if any(isinstance(a, Predator) for a in cell_agents):
                    continue

                # pusta albo z gupikiem
                self.grid.place_agent(predator, pos)
                placed = True
                break

            # nie znaleziono miejsca to przerywamy
            if not placed:
                break

        self.reproduce()

    def reproduce(self):
        females = [a for a in self.agents if isinstance(a, Individual) and a.sex == "F"]  

        for female in females:
            neighbors = self.grid.get_neighbors(female.pos, moore=True, include_center=False) #bierze agentow w sasiedztwie
            males = [a for a in neighbors if isinstance(a, Individual) and a.sex == "M"]
            if not males:
                continue

            # father = max(males, key=lambda m: m.N_orange) #wybor partnera na podstawie jak dla drapieznika 

            father = males[0]
            for male in males:
                score_tmp = female.score_males(male)
                score_father = female.score_males(father)
                if score_tmp > score_father:
                    father = male

            if self.random.random() >= self.reproduction_prob: #prawdopodobienstwo kojarzenia
                continue
            #szuka miejsc dla dzieci 
            possible_positions = set(self.grid.get_neighborhood(female.pos, moore=True, include_center=True))
            possible_positions |= set(self.grid.get_neighborhood(father.pos, moore=True, include_center=True))
            free_positions = [pos for pos in possible_positions if self.grid.is_cell_empty(pos)]
            
            if not free_positions: #jak nie ma wolnych kratek to nie ma gdzie urodzic
                continue

            #dzieci i dziedziczenie cech    
            child_sex = self.random.choice(["M", "F"])
            child = Individual(self, child_sex)

            if child_sex == "M":# doklic tutaj podobnie reszte parametrow i dla samic tez , 5 procent roznicy
                child.N_orange = min(5, max(0, father.N_orange + self.random.choice([-1, 0, 1])))
                child.N_black = min(5, max(0, father.N_black + self.random.choice([-1, 0, 1])))
                child.body_size = min(4.0, max(1.5, father.body_size + self.random.choice([-0.5, 0, 0.5])))
                child.orange_area = min(0.5, max(0, father.orange_area + self.random.choice([-0.05, 0, 0.05])))
                child.black_area =  min(0.5, max(0, father.black_area + self.random.choice([-0.05, 0, 0.05])))

            elif child_sex == "F":
                child.preference_orange    = min(1.0, max(0, female.preference_orange + self.random.choice([-0.05, 0, 0.05])))
                child.preference_black     = min(1.0, max(0, female.preference_black + self.random.choice([-0.05, 0, 0.05])))
                child.preference_body_size = min(1.0, max(0, female.preference_body_size + self.random.choice([-0.05, 0, 0.05])))
                child.preference_N_orange  = min(1.0, max(0, female.preference_N_orange + self.random.choice([-0.05, 0, 0.05])))
                child.preference_N_black   = min(1.0, max(0, female.preference_N_black + self.random.choice([-0.05, 0, 0.05])))  

            self.grid.place_agent(child, self.random.choice(free_positions))
            self.births_last_step += 1
