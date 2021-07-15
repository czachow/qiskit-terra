import pandas as pd


def write_to_dataframe(total_result):
    columns = ["seed", "state", "ideal_count", "noise_count", \
               "ideal_time", "noise_time", "ideal_swaps_needed", "noise_swaps_needed"]
    df = pd.DataFrame(columns=columns)

    ideal_counts = total_result["ideal_counts"]
    noise_counts = total_result["noise_counts"]
    states = set(ideal_counts.keys()) | set(noise_counts.keys())
    for state in states:
        df.loc[len(df)] = [total_result["seed"], state, ideal_counts.get(state, 0), noise_counts.get(state, 0), \
                           total_result["ideal_time"], total_result["noise_time"], total_result["ideal_swaps_needed"], \
                           total_result["noise_swaps_needed"]]

    return df