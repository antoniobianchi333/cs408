import pandas as pd
import math
from rapidfuzz import process, fuzz

# Input file paths (replace with your actual paths)
group_file = "existing_group.csv"
classlist_file = "classlist.csv"
output_file = "final_groups.csv"

# Load CSVs
groups_df = pd.read_csv(group_file, sep="\t")  # your first file looks tab-delimited
classlist_df = pd.read_csv(classlist_file, sep="\t")  # adjust delimiter if needed

def find_full_name(name, candidates):
    for full_name in candidates:
        found = True
        for string in name:
            if not string in full_name:
                found = False
                break
        if found:
            return full_name
    return None

# Extract full student roster
all_students = set(classlist_df["Username"])
all_ids = dict(zip(classlist_df["Username"], classlist_df["Image"]))

# Step 1: Collect existing groups
final_groups = []
assigned = set()

for _, row in groups_df.iterrows():
    group = []
    
    # First student
    if pd.notna(row["What is your Purdue alias? (e.g. lin1963)"]):
        group.append(row["What is your Purdue alias? (e.g. lin1963)"])
    if pd.notna(row["2nd Student:  What is the Purdue alias (if exists) ?"]):
        group.append(row["2nd Student:  What is the Purdue alias (if exists) ?"])
    if pd.notna(row["3rd Student:  What is the Purdue alias (if exists) ?"]):
        group.append(row["3rd Student:  What is the Purdue alias (if exists) ?"])

    # Mark them as assigned
    for username in group:
        assigned.add(username)

    final_groups.append(group)

# Step 2: Find unassigned students
unassigned = [s for s in all_students if s not in assigned]

# Step 3: Fill existing groups up to 3 members
for group in final_groups:
    while len(group) < 3 and unassigned:
        group.append(unassigned.pop(0))

# Step 4: Create new groups from remaining students
for i in range(0, len(unassigned), 3):
    final_groups.append(unassigned[i:i+3])

# ---------------------------
# NEW: Step 5 - Detect duplicates
# ---------------------------
seen = set()
duplicates = set()

for group in final_groups:
    for username in group:
        if username in seen:
            duplicates.add(username)
        else:
            seen.add(username)

if duplicates:
    print("Duplicate usernames detected across groups:")
    for d in duplicates:
        print(f"  - {d}")
else:
    print("No duplicate usernames detected.")

# Step 6: Save output in requested format
with open(output_file, "w") as f:
    f.write("GROUP_NUMBER,NAME_A,ID_A,NAME_B,ID_B,NAME_C,ID_C\n")
    for i, group in enumerate(final_groups, start=1):
        row = [str(i)]
        for username in group:
            row.append(all_ids.get(username, "UNKNOWN_NAME"))
            row.append(username)
        f.write(",".join(row) + "\n")

print(f"Groups saved to {output_file}")
