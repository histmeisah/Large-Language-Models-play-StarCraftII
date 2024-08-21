import os
import json
import pandas as pd
import shutil
import ast

"""
Main code for calculating StarCraft II game performance metrics
"""


def parse_game_time(time_str):
    """
    Convert game time string to seconds.

    Args:
    time_str (str): Game time in format 'MM:SS'

    Returns:
    int: Total seconds
    """
    try:
        minutes, seconds = map(int, time_str.split(':'))
        return minutes * 60 + seconds
    except ValueError as e:
        print(f"Error parsing time string: {time_str} - Error message: {e}")
        return 0


def extract_specific_resource_info(json_entry):
    """
    Extract relevant resource information from a JSON log entry.

    Args:
    json_entry (dict): A single log entry in JSON format

    Returns:
    dict: Extracted resource information
    """
    resource_info = json_entry.get("resource", {})
    return {
        "game_time": resource_info.get("game_time", "N/A"),
        "mineral": int(resource_info.get("mineral", 0)),
        "gas": int(resource_info.get("gas", 0)),
        "supply_left": int(resource_info.get("supply_left", 0)),
        "supply_cap": int(resource_info.get("supply_cap", 0)),
        "supply_used": int(resource_info.get("supply_used", 0))
    }


def calculate_population_block_time(log_entries):
    """
    Calculate the total time when population was maxed out (supply blocked).

    Args:
    log_entries (list): List of log entries

    Returns:
    tuple: (total_block_time, total_game_time)
    """
    total_game_time = 0
    total_block_time = 0
    population_maxed = False

    for entry in log_entries:
        info = extract_specific_resource_info(entry)
        game_time = parse_game_time(info["game_time"])
        supply_left = info["supply_left"]
        supply_used = info["supply_used"]

        if supply_left == 0 and not population_maxed:
            total_block_time += game_time - total_game_time

        total_game_time = game_time

        if supply_used >= 194:  # Assuming 194 is the max population
            population_maxed = True
            break
    return total_block_time, total_game_time


def calculate_population_utilization(log_entries):
    """
    Calculate the average population utilization throughout the game.

    Args:
    log_entries (list): List of log entries

    Returns:
    float: Average population utilization
    """
    total_utilization = 0
    count = 0

    for entry in log_entries:
        info = extract_specific_resource_info(entry)
        supply_cap = info["supply_cap"]
        supply_used = info["supply_used"]

        if supply_cap > 0:
            utilization = supply_used / supply_cap
            total_utilization += utilization
            count += 1

    return total_utilization / count if count > 0 else 0


def calculate_resource_utilization(log_entries):
    """
    Calculate the total resources collected until max population is reached.

    Args:
    log_entries (list): List of log entries

    Returns:
    tuple: (total_minerals, total_gas)
    """
    total_minerals = 0
    total_gas = 0
    population_maxed = False

    for entry in log_entries:
        info = extract_specific_resource_info(entry)
        supply_used = info["supply_used"]
        mineral = info["mineral"]
        gas = info["gas"]

        total_minerals += mineral
        total_gas += gas

        if supply_used >= 194:
            population_maxed = True
            break

    return total_minerals, total_gas


def calculate_total_possible_tech(log_entries):
    """
    Calculate the total number of possible technologies in the game.

    Args:
    log_entries (list): List of log entries

    Returns:
    int: Total number of possible technologies
    """
    total_possible_tech = set()
    for entry in log_entries:
        building_info = entry.get('building', {})
        research_info = entry.get('research', {})

        total_possible_tech.update(building_info.keys())
        for building, researches in research_info.items():
            total_possible_tech.update(f"{building}_{research}" for research in researches.keys())
    print("total_possible_tech:", len(total_possible_tech))
    return len(total_possible_tech)


def calculate_tech_rate(log_entries):
    """
    Calculate the maximum technology development rate achieved in the game.

    Args:
    log_entries (list): List of log entries

    Returns:
    float: Maximum technology rate achieved
    """
    total_possible_tech = calculate_total_possible_tech(log_entries)
    max_tech_rate = 0

    for entry in log_entries:
        building_info = entry.get('building', {})
        research_info = entry.get('research', {})

        completed_tech = sum(1 for count in building_info.values() if count > 0) + \
                         sum(1 for researches in research_info.values() for status in researches.values() if
                             status == 1)

        current_tech_rate = completed_tech / total_possible_tech if total_possible_tech else 0
        max_tech_rate = max(max_tech_rate, current_tech_rate)

    return max_tech_rate


def process_raw_observation_file(file_path):
    """
    Process the raw observation JSON file and return a list of processed entries.

    Args:
    file_path (str): Path to the raw observation JSON file

    Returns:
    list: Processed log entries
    """
    processed_entries = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip() == "[]":
                continue
            try:
                json_entry = json.loads(line)
                for key in json_entry:
                    if isinstance(json_entry[key], str):
                        json_entry[key] = ast.literal_eval(json_entry[key].replace("'", "\""))
                processed_entries.append(json_entry)
            except json.JSONDecodeError:
                print(f"JSON parsing error: {line}")
            except ValueError:
                print(f"Value conversion error: {line}")
    return processed_entries


def analyze_entry(entry):
    """
    Extract and analyze required information from a log entry.

    Args:
    entry (dict): A single log entry

    Returns:
    tuple: Various information extracted from the entry
    """
    resource_info = entry.get('resource', {})
    building_info = entry.get('building', {})
    unit_info = entry.get('unit', {})
    planning_info = entry.get('planning', {})
    research_info = entry.get('research', {})
    enemy_info = entry.get('enemy', {})

    return resource_info, building_info, unit_info, planning_info, research_info, enemy_info


def analyze_research(research_info):
    """
    Analyze research information from a log entry.

    Args:
    research_info (dict): Research information from a log entry

    Returns:
    dict: Processed research information
    """
    all_research = {}

    for building, researches in research_info.items():
        for research in researches.keys():
            key = f"{research}"
            all_research[key] = researches[research]

    return all_research


def process_log_files_and_calculate_indicators(src_path, dst_path, copy_flag=False):
    """
    Main function to process log files and calculate game performance indicators.

    Args:
    src_path (str): Source path for log files
    dst_path (str): Destination path for output Excel file
    copy_flag (bool): Flag to indicate if files should be copied (unused in this version)
    """
    data = []

    for folder in os.listdir(src_path):
        folder_path = os.path.join(src_path, folder)
        if os.path.isdir(folder_path):
            raw_observation_file = os.path.join(folder_path, "raw_observation.json")
            if os.path.exists(raw_observation_file):
                log_entries = process_raw_observation_file(raw_observation_file)

                total_block_time, total_game_time = calculate_population_block_time(log_entries)
                total_minerals, total_gas = calculate_resource_utilization(log_entries)
                avg_utilization = calculate_population_utilization(log_entries)
                tech_rate = calculate_tech_rate(log_entries)

                last_supply_used = log_entries[-1].get('resource', {}).get('supply_used', 0) if log_entries else 0

                pop_block_ratio = total_block_time / total_game_time if total_game_time > 0 else 0
                resource_utilization_ratio = (
                                                         total_minerals + total_gas) / total_game_time if total_game_time > 0 else 0

                data.append({
                    "Log Name": folder,
                    "Population Block Ratio": pop_block_ratio,
                    "Resource Utilization Ratio": resource_utilization_ratio,
                    "Average Population Utilization": avg_utilization,
                    "Tech Rate": tech_rate,
                    "Last Supply Used": last_supply_used
                })

    df = pd.DataFrame(data)
    excel_path = os.path.join(dst_path, "log_analysis.xlsx")
    df.to_excel(excel_path, index=False)
    print("Excel file generated:", excel_path)


# Set folder paths and call the main function
# Base path where the raw StarCraft II log files are stored
# This directory should contain subdirectories, each with a "raw_observation.json" file
base_path = r""# your log data path

# Destination path where the output Excel file will be saved
# In this case, it's the same as the base_path, but it could be different if needed
destination_path = r""# save the excel file path

# Call the main function to process log files and generate the Excel report
process_log_files_and_calculate_indicators(base_path, destination_path)