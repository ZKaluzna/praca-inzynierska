import solara
import numpy as np
import matplotlib.pyplot as plt

from mesa.visualization import SolaraViz
from mesa.visualization.components import make_space_component

from model import PopulationModel, Predator, Individual

def guppy_portrayal(agent):
    if isinstance(agent, Predator):
        return {"color": "red", "marker": "x", "size": 10}

    if agent.sex == "M":
        return {"color": "blue", "marker": "o", "size": 6}
    else:
        return {"color": "pink", "marker": "o", "size": 6}


def food_heatmap(model: PopulationModel):
    data = np.array(model.food, dtype=float)

    fig, ax = plt.subplots()
    ax.imshow(data, origin="lower", vmin=0, vmax=model.food_max)
    ax.set_title("Jedzenie w środowisku")
    ax.set_xticks([])
    ax.set_yticks([])

    return solara.FigureMatplotlib(fig)


def stats_panel(model: PopulationModel):
    males = [
        a for a in model.agents
        if isinstance(a, Individual) and a.sex == "M"
    ]
    females = [
        a for a in model.agents
        if isinstance(a, Individual) and a.sex == "F"
    ]

    guppies = [
        a for a in model.agents
        if isinstance(a, Individual)
    ]

    
    predators = [a for a in model.agents if isinstance(a, Predator)]


    avg_energy = (sum(g.energy for g in guppies) / len(guppies) if guppies else 0)


    avg_orange = (
        sum(m.N_orange for m in males) / len(males)
        if males else 0
    )

    avg_black = (
        sum(m.N_black for m in males) / len(males)
        if males else 0
    )

    avg_food = sum(sum(row) for row in model.food) / (model.grid.width * model.grid.height)

    p = model.params

    return solara.Markdown(
        f"""
## Populacja
- Gupiki: {len(males) + len(females)}
- Samce: {len(males)}
- Samice: {len(females)}
- Drapieżniki: {len(predators)}
- Śr. N_orange (samce): {avg_orange:.2f}
- Śr. N_black (samce): {avg_black:.2f}

## Środowisko
- Śr. jedzenie na kratkę: {avg_food:.2f}

## Przebieg
- Krok: {model.step_count}
- Urodzenia (ostatni krok): {model.births_last_step}
- Zgony (ostatni krok): {model.deaths_last_step}
- Śr. energia gupików: {avg_energy:.2f}


## Parametry (food)
- Maksymalnie jedzenia: {p["food_max"]}
- jednostka regeneracji (bez gupika x2): {p["food_regen"]}
- Jednostka zjadana: {p["food_eat"]}
"""
    )


@solara.component
def Page():
    model = PopulationModel()

    space_component = make_space_component(agent_portrayal=guppy_portrayal,backend="matplotlib",)

    return SolaraViz(
        model,
        components=[
            (space_component, 0),
            (food_heatmap, 1),
            (stats_panel, 2),
        ],
        name= "Model wieloagentowy/heatmapa/statystyki",
        play_interval=200,
        render_interval=1,
    )
