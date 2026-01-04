import pandas as pd

# ----------------------------
# File paths
# ----------------------------
final_groups_file = "lab2_groups.csv"       # your current final_groups CSV
enroll_file = "lab2_final_enrollments.csv"       # output enrollment CSV
group_prefix = "Lab 2 - Group_1360116_453870_"

# ----------------------------
# Load final_groups CSV
# ----------------------------
df = pd.read_csv(final_groups_file)

# Strip whitespace from column names
df.columns = df.columns.str.strip()

# ----------------------------
# Step 1: Prepare enrollment rows
# ----------------------------
enroll_rows = []

for idx, row in df.iterrows():
    group_number = row['GROUP_NUMBER']
    if pd.isna(group_number):
        continue  # skip invalid rows

    group_code = f"{group_prefix}{int(group_number)}"

    for col in ['ID_A', 'ID_B', 'ID_C', 'ID_D']:
        username = row[col]
        if pd.notna(username) and str(username).strip() != "":
            enroll_rows.append({
                "ACTION": "ENROLL",
                "Username": str(username).strip(),
                "Org Defined ID": "",
                "Group Name": "",
                "Group Code": group_code
            })

# ----------------------------
# Step 2: Save enrollment CSV
# ----------------------------
enroll_df = pd.DataFrame(enroll_rows)

# Brightspace requires no header
enroll_df.to_csv(enroll_file, index=False, header=False)

print(f"✅ Enrollment CSV saved to {enroll_file}")
