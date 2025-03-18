from graffitiai import GraffitiAI
from pyfiglet import Figlet
from rich.panel import Panel
from rich.prompt import Prompt
from questionary import select
import questionary

from polytope_app.utils import custom_style, keyword_map, write_on_the_wall

__all__ = [
    'conjecture_mode',
]


def probability_distribution(target, df, num_features=4):
    import random
    import numpy as np
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df = df[numeric_cols]

    # Ensure the target exists in the dataframe
    if target not in df.columns:
        raise ValueError(f"Target {target} not in numeric columns!")

    df = df.fillna(0)

    # Split features and target
    X = df.drop(columns=[target])
    y = df[target]

    # Fix potential NaN values and normalize
    X = X.fillna(0)
    X = (X - X.mean()) / X.std()
    y = y.fillna(0)
    y = (y - y.mean()) / y.std()

    # Compute absolute Pearson correlation
    correlations = X.corrwith(y).abs()

    # Convert correlations into a probability distribution
    prob_dist = correlations / correlations.sum()

    # Remove problematic entries
    prob_dist = prob_dist.replace([np.inf, -np.inf], np.nan).dropna()

    # Renormalize
    prob_dist /= prob_dist.sum()

    # Now sample safely:
    return list(set(random.choices(
        population=prob_dist.index,
        weights=prob_dist.values,
        k=num_features,
    )))

def conjecture_mode(graffiti, numerical_columns, console):
    """
    Runs the Graffiti AI in conjecture mode, allowing the user to enter a graph
    and then ask the AI to conjecture on a property of the polytope database.
    """
    console.print("[bold cyan]Welcome to Polytope AI Conjecture Mode![/bold cyan]")

    while True:
        # prompy the user to select a numerical property to conjecture on for them to scroll through and select.
        numerical_properties = numerical_columns
        target_property = questionary.select(
            "Select a numerical property to conjecture on:",
            choices=numerical_properties,
            style=custom_style,
        ).ask()
        target_property = [target_property]

        # prompt the user to increase complexity (if they want) from complexity 1 to 3.
        yes_no = questionary.select(
            "Would you like to increase the complexity level?",
            choices=["Yes", "No"],
            style=custom_style,
        ).ask()
        if yes_no == "Yes":
            # prompt to select the complexity level to increase to 1-3.
            complexity_level = questionary.select(
                "Select the complexity level to increase to:",
                choices=["1", "2", "3"],
                style=custom_style,
            ).ask()
            complexity_level = int(complexity_level)
            graffiti.set_complexity(avoid_columns=target_property, max_complexity=complexity_level)
            console.print(f"[bold cyan]Complexity level increased.[/bold cyan]")

        boolean_properties = graffiti.boolean_columns

        # prompt the user to conjecture, to start over, or to exit back to the main menu.
        while True:
            perform_conjecture = questionary.select(
                "Select an option:",
                choices=[
                    f"Conjecture on {target_property[0]}",
                    "Start over",
                    "Exit to main menu"
                ],
                style=custom_style,
            ).ask()

            if perform_conjecture == f"Conjecture on {target_property[0]}":
                # prompt the user to select the number of searches to perform.
                num_searches = questionary.text(
                    "Enter the number of searches to perform:",
                    style=custom_style,
                ).ask()
                num_searches = int(num_searches)

                for _ in range(num_searches):
                    print(f"Searching stage {_ + 1} of {num_searches} search processes....")
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(1, 1),
                        lower_b_max=3,
                        lower_b_min=-3,
                        upper_b_max=3,
                        upper_b_min=-3,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(1, 1),
                        lower_b_max=2,
                        lower_b_min=-2,
                        upper_b_max=2,
                        upper_b_min=-2,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(1, 1),
                        lower_b_max=1,
                        lower_b_min=-1,
                        upper_b_max=1,
                        upper_b_min=-1,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                    # other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    # graffiti.conjecture(
                    #     target_invariants=target_property,
                    #     hypothesis=boolean_properties,
                    #     other_invariants = other_invariants,
                    #     complexity_range=(1, 1),
                    #     lower_b_max=None,
                    #     lower_b_min=None,
                    #     upper_b_max=None,
                    #     upper_b_min=None,
                    #     W_lower_bound=None,
                    #     W_upper_bound=None,
                    # )
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(2, 2),
                        lower_b_max=3,
                        lower_b_min=-3,
                        upper_b_max=3,
                        upper_b_min=-3,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(2, 2),
                        lower_b_max=2,
                        lower_b_min=-2,
                        upper_b_max=2,
                        upper_b_min=-2,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(2, 2),
                        lower_b_max=1,
                        lower_b_min=-1,
                        upper_b_max=1,
                        upper_b_min=-1,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                    # other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    # graffiti.conjecture(
                    #     target_invariants=target_property,
                    #     hypothesis=boolean_properties,
                    #     other_invariants = other_invariants,
                    #     complexity_range=(1, 2),
                    #     lower_b_max=None,
                    #     lower_b_min=None,
                    #     upper_b_max=None,
                    #     upper_b_min=None,
                    #     W_lower_bound=None,
                    #     W_upper_bound=None,
                    # )
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(3, 3),
                        lower_b_max=3,
                        lower_b_min=-3,
                        upper_b_max=3,
                        upper_b_min=-3,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(3, 3),
                        lower_b_max=2,
                        lower_b_min=-2,
                        upper_b_max=2,
                        upper_b_min=-2,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(3, 3),
                        lower_b_max=1,
                        lower_b_min=-1,
                        upper_b_max=1,
                        upper_b_min=-1,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                    # other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    # graffiti.conjecture(
                    #     target_invariants=target_property,
                    #     hypothesis=boolean_properties,
                    #     other_invariants = other_invariants,
                    #     complexity_range=(1, 3),
                    #     lower_b_max=None,
                    #     lower_b_min=None,
                    #     upper_b_max=None,
                    #     upper_b_min=None,
                    #     W_lower_bound=None,
                    #     W_upper_bound=None,
                    # )
                console.print("[bold cyan]Conjecture complete![/bold cyan]")
                # Display the conjecture results using write on the wall with search = True
                # write_on_the_wall(graffiti, target_invariants=target_property, search=True)
                # view_conjectures(graffiti, target_invariants=target_property, search=True, console=console)
                write_on_the_wall(graffiti, numerical_columns, target_invariants=target_property, search=True, console=console)

            elif perform_conjecture == "Start over":
                break
            else:
                return

