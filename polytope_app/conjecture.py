from graffitiai import GraffitiAI
from pyfiglet import Figlet
import questionary

from polytope_app.utils import custom_style

__all__ = [
    'write_on_the_wall',
    'probability_distribution',
    'conjecture_mode',
]


def convert_hypothesis(hypothesis):

    if hypothesis == "None":
        return "simple polytope graph"
    elif hypothesis == "simple_polytope_graph":
        return "simple polytope graph"
    elif hypothesis == "connected_and_bipartite":
        return "simple polytope graph without odd cycles"
    elif hypothesis == "simple_polytope_graph_with_p6_greater_than_zero":
        return "simple polytope graph with p_6 > 0"
    elif hypothesis == "is_at_free ":
        return "simple asteroidal triple free polytope graph"
    elif hypothesis == "simple_polytope_graph_with_p6_zero":
        return "simple polytope graph with p_6 = 0"
    elif hypothesis == "zeros_clustered(p_vector)":
        return "simple polytope graph with clustered zeros in p_vector"
    else:
        return ""


def write_on_the_wall(agent, target_invariants, search=True):
        """
        Display generated upper and lower conjectures for specified target invariants,
        with a more detailed and user-friendly view, including:
        - Percentage of hypothesis objects that are sharp.
        - Neatly formatted sharp instances in columns.
        - Analysis of common properties among the sharp instances (if any exist).

        Args:
            target_invariants (list, optional): List of target invariants to display.
                If None, displays conjectures for all invariants.

        Example:
            >>> ai.write_on_the_wall(target_invariants=['independence_number'])
        """
        fig = Figlet(font='slant')

        # Helper: Get subset of rows corresponding to sharp instances.
        def get_sharp_subset(df, sharp_ids):
            """
            If 'name' is a column in df, filter rows where df['name'] is in sharp_ids;
            otherwise, assume sharp_ids are indices.
            """
            if 'name' in df.columns:
                return df[df['name'].isin(sharp_ids)]
            else:
                return df.loc[sharp_ids]

        # Helper: Format a list of sharp instances into columns.
        def format_sharp_instances(instances, num_columns=4, indent="    "):
            items = sorted(str(item) for item in instances)
            if not items:
                return ""
            max_width = max(len(item) for item in items)
            rows = (len(items) + num_columns - 1) // num_columns
            formatted_rows = []
            for row in range(rows):
                row_items = []
                for col in range(num_columns):
                    idx = col * rows + row
                    if idx < len(items):
                        row_items.append(items[idx].ljust(max_width))
                formatted_rows.append(indent + "   ".join(row_items))
            return "\n".join(formatted_rows)

        # Helper: Find common constant boolean properties.
        def find_common_boolean_properties(df, sharp_ids, boolean_columns):
            subset = get_sharp_subset(df, sharp_ids)
            common_props = {}
            for col in boolean_columns:
                unique_vals = subset[col].unique()
                if len(unique_vals) == 1:
                    common_props[col] = unique_vals[0]
            return common_props

        # Helper: Find common numeric properties.
        def find_common_numeric_properties(df, sharp_ids, numeric_columns):
            subset = get_sharp_subset(df, sharp_ids)
            common_props = {}
            for col in numeric_columns:
                values = subset[col].dropna()
                props = []
                if (values == 0).all():
                    props.append("all zero")
                # if (values != 0).all():
                #     props.append("all nonzero")
                # Check even/odd if the column is integer-like.
                # if pd.api.types.is_integer_dtype(values) or all(float(v).is_integer() for v in values):
                #     if (values % 2 == 0).all():
                #         props.append("even")
                #     if (values % 2 == 1).all():
                #         props.append("odd")
                common_props[col] = props
            return common_props

        # Print a fancy title.
        title = fig.renderText("Graffiti AI")
        print(title)
        print("Author: Randy R. Davila, PhD")
        print("Automated Conjecturing since 2017")
        print("=" * 80)
        print()

        if not hasattr(agent, 'conjectures') or not agent.conjectures:
            print("No conjectures generated yet!")
            return

        # Use all available target invariants if none are provided.
        if target_invariants is None:
            target_invariants = list(agent.conjectures.keys())

        # Iterate through each target invariant.
        for target in target_invariants:
            conj_data = agent.conjectures.get(target, {})
            upper_conj = conj_data.get("upper", [])
            lower_conj = conj_data.get("lower", [])
            equal_conj = conj_data.get("equals", [])

            print(f"Target Invariant: {target}")
            print("-" * 40)

            # Display equal conjectures if any exist.
            if equal_conj:
                print("\nEqual Conjectures:")
                for i, conj in enumerate(equal_conj, start=1):
                    print(f"\nConjecture {i}:")
                    print("------------")
                    hypothesis = convert_hypothesis(conj.hypothesis)
                    conclusion = conj._set_conclusion()
                    statement = f"For any {hypothesis}, {conclusion}."
                    print(f"Statement: {statement}")
                    # print(f"Statement: {conj.full_expr}")
                    print("Details:")
                    # print(f"  Keywords:")
                    # for keyword in conj.keywords:
                    #     print(f"    {keyword}")
                    print(f"  Target Invariant: {conj.target}")
                    print(f"  Bound Type: {conj.bound_type}")
                    print(f"  Hypothesis: Any {hypothesis}")
                    print(f"  Conclusion: {conj._set_conclusion()}")

            # Display Upper Bound Conjectures.
            print("\nUpper Bound Conjectures:")
            if upper_conj:
                for i, conj in enumerate(upper_conj, start=1):
                    if conj.touch > 0 and i < 10:
                        print(f"\nConjecture {i}:")
                        print("------------")
                        # print(f"Statement: {conj.full_expr}")
                        hypothesis = convert_hypothesis(conj.hypothesis)
                        conclusion = conj._set_conclusion()
                        statement = f"For any {hypothesis}, {conclusion}."
                        print(f"Statement: {statement}")
                        print("Details:")
                        # print(f"  Keywords:")
                        # for keyword in conj.keywords:
                        #     print(f"    {keyword}")
                        print(f"  Target Invariant: {conj.target}")
                        print(f"  Bound Type: {conj.bound_type}")
                        print(f"  Hypothesis: Any {hypothesis}")
                        print(f"  Conclusion: {conj._set_conclusion()}")
                        if hasattr(conj, 'complexity') and conj.complexity is not None:
                            print(f"  Complexity: {conj.complexity}")
                        if conj.touch > 0:
                            if conj.touch > 1:
                                print(f"  Sharp on {conj.touch} objects.")
                            else:
                                print("  Sharp on 1 object.")
                        else:
                            print("  Inequality is strict.")
                        if hasattr(conj, 'sharp_instances') and conj.sharp_instances:
                            print("  Sharp Instances:")
                            print(format_sharp_instances(conj.sharp_instances, num_columns=4))
                            if search:
                                # If knowledge_table is available, analyze common properties.
                                if hasattr(agent, 'knowledge_table'):
                                    sharp_ids = list(conj.sharp_instances)
                                    common_bool = (find_common_boolean_properties(agent.knowledge_table, sharp_ids, agent.boolean_columns)
                                                if hasattr(agent, 'boolean_columns') else {})
                                    common_numeric = (find_common_numeric_properties(agent.knowledge_table, sharp_ids, agent.original_numerical_columns)
                                                    if hasattr(agent, 'numerical_columns') else {})
                                    # common_ineq = (find_common_inequalities(agent.knowledge_table, sharp_ids, agent.numerical_columns)
                                    #             if hasattr(agent, 'numerical_columns') else [])
                                    if common_bool or common_numeric:
                                        print("  Common properties among sharp instances:")
                                        if common_bool:
                                            print("    Constant boolean columns:")
                                            for col, val in common_bool.items():
                                                print(f"      {col} == {val}")

                                        if common_numeric:
                                            print("    Common numeric properties:")
                                            for col, props in common_numeric.items():
                                                if props:
                                                    print(f"      {col}: {', '.join(props)}")
                                        else:
                                            print("    Common numeric properties:")
                                            print("      None")
                                    else:
                                        print("  No common properties found among sharp instances.")
                        # Calculate and display the percentage of hypothesis objects that are sharp.
                        if hasattr(agent, 'knowledge_table') and conj.hypothesis in agent.knowledge_table.columns:
                            hyp_df = agent.knowledge_table[agent.knowledge_table[conj.hypothesis] == True]
                            total_hyp = len(hyp_df)
                            if total_hyp > 0:
                                percent_sharp = 100 * conj.touch / total_hyp
                                print(f"  Percentage of hypothesis objects that are sharp: {percent_sharp:.1f}%")
                            else:
                                print("  No objects satisfy the hypothesis.")
                else:
                    print("  None")

            # Display Lower Bound Conjectures.
            print("\nLower Bound Conjectures:")
            if lower_conj:
                for i, conj in enumerate(lower_conj, start=1):
                    if conj.touch > 0 and i < 10:
                        print(f"\nConjecture {i}:")
                        print("------------")
                        hypothesis = convert_hypothesis(conj.hypothesis)
                        conclusion = conj._set_conclusion()
                        statement = f"For any {hypothesis}, {conclusion}."
                        print(f"Statement: {statement}")
                        # print(f"Statement: {conj.full_expr}")
                        print("Details:")
                        print(f"  Keywords:")
                        # for keyword in conj.keywords:
                        #     print(f"    {keyword}")
                        print(f"  Target Invariant: {conj.target}")
                        print(f"  Bound Type: {conj.bound_type}")
                        print(f"  Hypothesis: Any {hypothesis}")
                        print(f"  Conclusion: {conj._set_conclusion()}")
                        if hasattr(conj, 'complexity') and conj.complexity is not None:
                            print(f"  Complexity: {conj.complexity}")
                        if conj.touch > 0:
                            if conj.touch > 1:
                                print(f"  Sharp on {conj.touch} objects.")
                            else:
                                print("  Sharp on 1 object.")
                        else:
                            print("  Inequality is strict.")
                        if hasattr(conj, 'sharp_instances') and conj.sharp_instances:
                            print("  Sharp Instances:")
                            print(format_sharp_instances(conj.sharp_instances, num_columns=4))
                            if search:
                                if hasattr(agent, 'knowledge_table'):
                                    sharp_ids = list(conj.sharp_instances)
                                    common_bool = (find_common_boolean_properties(agent.knowledge_table, sharp_ids, agent.boolean_columns)
                                                if hasattr(agent, 'boolean_columns') else {})
                                    common_numeric = (find_common_numeric_properties(agent.knowledge_table, sharp_ids, agent.original_numerical_columns)
                                                    if hasattr(agent, 'numerical_columns') else {})
                                    # common_ineq = (find_common_inequalities(agent.knowledge_table, sharp_ids, agent.numerical_columns)
                                    #             if hasattr(agent, 'numerical_columns') else [])
                                    if common_bool or common_numeric:
                                        print("  Common properties among sharp instances:")
                                        if common_bool:
                                            print("    Constant boolean columns:")
                                            for col, val in common_bool.items():
                                                print(f"      {col} == {val}")
                                        if common_numeric:
                                            print("    Common numeric properties:")
                                            for col, props in common_numeric.items():
                                                if props:
                                                    print(f"      {col}: {', '.join(props)}")
                                        else:
                                            print("    Common numeric properties:")
                                            print("      None")
                                    else:
                                        print("  No common properties found among sharp instances.")
                        if hasattr(agent, 'knowledge_table') and conj.hypothesis in agent.knowledge_table.columns:
                            hyp_df = agent.knowledge_table[agent.knowledge_table[conj.hypothesis] == True]
                            total_hyp = len(hyp_df)
                            if total_hyp > 0:
                                percent_sharp = 100 * conj.touch / total_hyp
                                print(f"  Percentage of hypothesis objects that are sharp: {percent_sharp:.1f}%")
                            else:
                                print("  No objects satisfy the hypothesis.")
                else:
                    print("  None")

            print("\n" + "=" * 80 + "\n")

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

def conjecture_mode(console):
    """
    Runs the Graffiti AI in conjecture mode, allowing the user to enter a graph
    and then ask the AI to conjecture on a property of the polytope database.
    """
    graffiti = GraffitiAI()
    console.print("[bold cyan]Welcome to Graffiti AI Conjecture Mode![/bold cyan]")

    graffiti.read_csv("Simple_Polytope_Data/simple_polytope_properties.csv")
    graffiti.vectorize(['p_vector'])
    graffiti.add_statistics(['p_vector'])
    graffiti.knowledge_table['p_3'] = graffiti.knowledge_table['p_vector'].apply(lambda x: x[0])
    graffiti.knowledge_table['p_4'] = graffiti.knowledge_table['p_vector'].apply(lambda x: x[1] if len(x) > 1 else 0)
    graffiti.knowledge_table['p_5'] = graffiti.knowledge_table['p_vector'].apply(lambda x: x[2] if len(x) > 2 else 0)
    graffiti.knowledge_table['p_6'] = graffiti.knowledge_table['p_vector'].apply(lambda x: x[3] if len(x) > 3 else 0)
    graffiti.knowledge_table['p_7'] = graffiti.knowledge_table['p_vector'].apply(lambda x: x[4] if len(x) > 4 else 0)
    graffiti.knowledge_table['sum(p_vector)'] = graffiti.knowledge_table['p_vector'].apply(lambda x: sum(x))

    # reset all numerical columns of the knowledge_table
    numerical_columns = graffiti.knowledge_table.select_dtypes(include=['number']).columns.tolist()

    # drop the columns that are not needed
    graffiti.drop_columns(['p_vector', 'adjacency_matrix', 'size'])

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
            graffiti.set_complexity(avoid_columns=target_property, max_complexity=1)
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
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(1, 1),
                        lower_b_max=None,
                        lower_b_min=None,
                        upper_b_max=None,
                        upper_b_min=None,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(1, 2),
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
                        complexity_range=(1, 2),
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
                        complexity_range=(1, 2),
                        lower_b_max=1,
                        lower_b_min=-1,
                        upper_b_max=1,
                        upper_b_min=-1,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(1, 2),
                        lower_b_max=None,
                        lower_b_min=None,
                        upper_b_max=None,
                        upper_b_min=None,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(1, 3),
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
                        complexity_range=(1, 3),
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
                        complexity_range=(1, 3),
                        lower_b_max=1,
                        lower_b_min=-1,
                        upper_b_max=1,
                        upper_b_min=-1,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                    other_invariants = probability_distribution(target_property[0], graffiti.knowledge_table)
                    graffiti.conjecture(
                        target_invariants=target_property,
                        hypothesis=boolean_properties,
                        other_invariants = other_invariants,
                        complexity_range=(1, 3),
                        lower_b_max=None,
                        lower_b_min=None,
                        upper_b_max=None,
                        upper_b_min=None,
                        W_lower_bound=None,
                        W_upper_bound=None,
                    )
                console.print("[bold cyan]Conjecture complete![/bold cyan]")
                # Display the conjecture results using write on the wall with search = True
                write_on_the_wall(graffiti, target_invariants=target_property, search=True)

            elif perform_conjecture == "Start over":
                break
            else:
                return
