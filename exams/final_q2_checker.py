def evaluate_P(a, b, c):
    """
    Evaluates P = (a AND NOT b) OR c
    """
    return (a and not b) or c

def check_predicate_coverage(test_set):
    seen_true = False
    seen_false = False
    
    print(f"{'Input Assignments':<30} | {'P (Result)':<10}")
    print("-" * 45)

    for case in test_set:
        a, b, c = case['a'], case['b'], case['c']
        result = evaluate_P(a, b, c)
        
        # Track if we have seen True or False outcomes
        if result is True:
            seen_true = True
        else:
            seen_false = True
            
        # Format input for display
        input_str = f"{{a={str(a)[0]}, b={str(b)[0]}, c={str(c)[0]}}}"
        print(f"{input_str:<30} | {str(result):<10}")

    print("-" * 45)
    
    # Verdict
    if seen_true and seen_false:
        print(">>> Predicate Coverage: SATISFIED (Both True and False outcomes observed)")
    else:
        print(">>> Predicate Coverage: FAILED (Missing either a True or False outcome)")
        if not seen_true:
            print("    (Missing a case where P = True)")
        if not seen_false:
            print("    (Missing a case where P = False)")


def check_clause_coverage(test_set):
    """
    Checks if a test set satisfies Clause Coverage for variables a, b, c.
    Requirement: Each variable must be True at least once and False at least once.
    """
    # Sets to track the values we have seen for each variable
    observed_values = {
        'a': set(),
        'b': set(),
        'c': set()
    }

    print(f"{'Test Case':<10} | {'a':<6} | {'b':<6} | {'c':<6}")
    print("-" * 40)

    for i, case in enumerate(test_set):
        a, b, c = case['a'], case['b'], case['c']
        
        # Record the values
        observed_values['a'].add(a)
        observed_values['b'].add(b)
        observed_values['c'].add(c)
        
        # Display the row
        print(f"Case {i+1:<5} | {str(a):<6} | {str(b):<6} | {str(c):<6}")

    print("-" * 40)
    print("Coverage Analysis:")

    # Check each variable
    all_clauses_covered = True
    
    for var in ['a', 'b', 'c']:
        has_true = True in observed_values[var]
        has_false = False in observed_values[var]
        
        if has_true and has_false:
            status = "PASS"
        else:
            status = "FAIL"
            all_clauses_covered = False
            missing = []
            if not has_true: missing.append("True")
            if not has_false: missing.append("False")
            status += f" (Missing: {', '.join(missing)})"
            
        print(f"  Variable '{var}': {status}")

    print("-" * 40)
    
    # Final Verdict
    if all_clauses_covered:
        print(">>> Clause Coverage: SATISFIED")
    else:
        print(">>> Clause Coverage: FAILED")

def check_racc(test_set):
    """
    Checks if a test set satisfies Restricted Active Clause Coverage (RACC)
    for P = (a AND NOT b) OR c.
    """
    
    # 1. Define Boolean Differences (derived in previous steps)
    # These determine if a variable is "active" (capable of changing the output)
    def is_a_active(b, c): return (not b) and (not c)  # p_a = ~b & ~c
    def is_b_active(a, c): return a and (not c)        # p_b = a & ~c
    def is_c_active(a, b): return (not a) or b         # p_c = ~a | b

    variables = ['a', 'b', 'c']
    satisfied = {v: False for v in variables}
    
    print(f"{'Variable':<10} | {'Status':<10} | {'Satisfying Pair (Indices)'}")
    print("-" * 55)

    # 2. Iterate through each variable to find a valid RACC pair
    for var in variables:
        # We need to compare every test case against every other test case
        for i in range(len(test_set)):
            for j in range(i + 1, len(test_set)):
                t1 = test_set[i]
                t2 = test_set[j]
                
                # Condition A: The target variable MUST toggle
                if t1[var] == t2[var]:
                    continue

                # Condition B: All OTHER variables must be CONSTANT (Restricted)
                others_constant = True
                for other_var in variables:
                    if other_var != var and t1[other_var] != t2[other_var]:
                        others_constant = False
                        break
                if not others_constant:
                    continue

                # Condition C: The variable must be ACTIVE
                # Since minor variables are constant, we only need to check activation 
                # on one of the cases (it will be the same for both).
                active = False
                if var == 'a':
                    active = is_a_active(t1['b'], t1['c'])
                elif var == 'b':
                    active = is_b_active(t1['a'], t1['c'])
                elif var == 'c':
                    active = is_c_active(t1['a'], t1['b'])
                
                if active:
                    satisfied[var] = True
                    # Log the successful pair (using 1-based indexing for readability)
                    print(f"{var:<10} | {'PASS':<10} | Cases {i+1} & {j+1}")
                    break # Stop looking for this variable, we found a pair
            
            if satisfied[var]: break

        if not satisfied[var]:
             print(f"{var:<10} | {'FAIL':<10} | No valid pair found")

    print("-" * 55)
    
    # Final Verdict
    if all(satisfied.values()):
        print(">>> Restricted Active Clause Coverage: SATISFIED")
    else:
        print(">>> Restricted Active Clause Coverage: FAILED")

def check_cacc(test_set):
    """
    Verifies Correlated Active Clause Coverage (CACC) for P = (a AND NOT b) OR c.
    
    CACC Requirements for a variable 'v':
    1. Find a pair of test cases (t1, t2).
    2. 'v' must toggle values between t1 and t2.
    3. The output P must toggle values.
    4. The boolean difference p_v must be True for BOTH t1 and t2.
       (Meaning 'v' is the determining factor in both contexts).
    """

    # --- 1. Define Logic Helpers ---
    
    # The main function P
    def evaluate_P(val_a, val_b, val_c): 
        return (val_a and not val_b) or val_c

    # The Boolean Differences (Activation Conditions)
    # p_a is True if b=False AND c=False
    def is_a_active(b, c): return (not b) and (not c)
    
    # p_b is True if a=True AND c=False
    def is_b_active(a, c): return a and (not c)
    
    # p_c is True if a=False OR b=True (equivalent to a -> b)
    def is_c_active(a, b): return (not a) or b

    variables = ['a', 'b', 'c']
    satisfied = {v: False for v in variables}
    
    print(f"{'Variable':<10} | {'Status':<10} | {'Pair Found'} | {'Logic Check (p_v)'}")
    print("-" * 75)

    # --- 2. Iterate through variables to find valid CACC pairs ---
    for var in variables:
        found_pair = False
        
        # Compare every unique pair of test cases
        for i in range(len(test_set)):
            for j in range(i + 1, len(test_set)):
                t1 = test_set[i]
                t2 = test_set[j]
                
                # Check 1: Does the variable toggle?
                if t1[var] == t2[var]: 
                    continue
                
                # Check 2: Does the output P toggle?
                p1 = evaluate_P(t1['a'], t1['b'], t1['c'])
                p2 = evaluate_P(t2['a'], t2['b'], t2['c'])
                if p1 == p2:
                    continue

                # Check 3: Is the variable ACTIVE in BOTH cases?
                active1, active2 = False, False
                
                if var == 'a': 
                    active1 = is_a_active(t1['b'], t1['c'])
                    active2 = is_a_active(t2['b'], t2['c'])
                elif var == 'b': 
                    active1 = is_b_active(t1['a'], t1['c'])
                    active2 = is_b_active(t2['a'], t2['c'])
                elif var == 'c': 
                    active1 = is_c_active(t1['a'], t1['b'])
                    active2 = is_c_active(t2['a'], t2['b'])
                
                if active1 and active2:
                    found_pair = True
                    # Format a logic string for display
                    logic_str = f"Active in both? Yes"
                    print(f"{var:<10} | {'PASS':<10} | Cases {i+1} & {j+1} | {logic_str}")
                    satisfied[var] = True
                    break # Stop looking for this variable
            
            if found_pair: break
        
        if not found_pair:
             print(f"{var:<10} | {'FAIL':<10} | None       | No pair found where {var} determines output")

    print("-" * 75)
    
    # Final Verdict
    if all(satisfied.values()):
        print(">>> Correlated Active Clause Coverage: SATISFIED")
    else:
        print(">>> Correlated Active Clause Coverage: FAILED")

def check_gacc(test_set):
    """
    Verifies General Active Clause Coverage (GACC) for P = (a AND NOT b) OR c.
    
    GACC Requirements for a variable 'v':
    1. Find a pair of test cases (t1, t2).
    2. 'v' must toggle values.
    3. The boolean difference p_v must be True for BOTH t1 and t2.
       (Note: We do NOT check if other variables are constant).
    """

    # --- 1. Define Logic Helpers ---
    
    # The Boolean Differences (Activation Conditions)
    # p_a is True if b=False AND c=False
    def is_a_active(b, c): return (not b) and (not c)
    
    # p_b is True if a=True AND c=False
    def is_b_active(a, c): return a and (not c)
    
    # p_c is True if a=False OR b=True
    def is_c_active(a, b): return (not a) or b

    variables = ['a', 'b', 'c']
    satisfied = {v: False for v in variables}
    
    print(f"{'Variable':<10} | {'Status':<10} | {'Pair Found'} | {'Context Change?'}")
    print("-" * 75)

    # --- 2. Iterate through variables to find valid GACC pairs ---
    for var in variables:
        found_pair = False
        
        for i in range(len(test_set)):
            for j in range(i + 1, len(test_set)):
                t1 = test_set[i]
                t2 = test_set[j]
                
                # Check 1: Does the variable toggle?
                if t1[var] == t2[var]: 
                    continue
                
                # Check 2: Is the variable ACTIVE in BOTH cases?
                active1, active2 = False, False
                
                if var == 'a': 
                    active1 = is_a_active(t1['b'], t1['c'])
                    active2 = is_a_active(t2['b'], t2['c'])
                elif var == 'b': 
                    active1 = is_b_active(t1['a'], t1['c'])
                    active2 = is_b_active(t2['a'], t2['c'])
                elif var == 'c': 
                    active1 = is_c_active(t1['a'], t1['b'])
                    active2 = is_c_active(t2['a'], t2['b'])
                
                if active1 and active2:
                    found_pair = True
                    satisfied[var] = True
                    
                    # Analyze if other variables changed (The GACC feature)
                    context_changed = "No"
                    for other_var in variables:
                        if other_var != var and t1[other_var] != t2[other_var]:
                            context_changed = "YES (Allowed in GACC)"
                            break
                            
                    print(f"{var:<10} | {'PASS':<10} | Cases {i+1} & {j+1} | {context_changed}")
                    break 
            
            if found_pair: break
        
        if not found_pair:
             print(f"{var:<10} | {'FAIL':<10} | None       | No pair where {var} is active in both")

    print("-" * 75)
    
    if all(satisfied.values()):
        print(">>> General Active Clause Coverage: SATISFIED")
    else:
        print(">>> General Active Clause Coverage: FAILED")

# --- Main Execution ---

# The specific set from your request:
# 1. {a=T, b=F, c=T}
# 2. {a=F, b=T, c=F}
input_assignments = [
    #{'a': True,  'b': True, 'c': True},     # 1
    #{'a': True,  'b': True, 'c': False},    # 2
    #{'a': True,  'b': False, 'c': True},    # 3
    #{'a': True,  'b': False, 'c': False},   # 4
    #{'a': False, 'b': True,  'c': True},    # 5
    #{'a': False, 'b': True,  'c': False},   # 6
    #{'a': False, 'b': False, 'c': True},    # 7
    #{'a': False, 'b': False, 'c': False}    # 8
]



# GACC
#    {'a': True,  'b': True, 'c': False},    # 2
#    {'a': True,  'b': False, 'c': False},   # 4
#    {'a': False, 'b': True,  'c': True},    # 5
#    {'a': False, 'b': False, 'c': False}    # 8

# GACC
#    {'a': True,  'b': True, 'c': False},    # 2
#    {'a': True,  'b': False, 'c': False},   # 4
#    {'a': False, 'b': False, 'c': True},    # 7
#    {'a': False, 'b': False, 'c': False}    # 8

# GACC
#    {'a': True,  'b': True, 'c': True},     # 1
#    {'a': True,  'b': True, 'c': False},    # 2
#    {'a': True,  'b': False, 'c': False},   # 4
#    {'a': False, 'b': False, 'c': False}    # 8





####################


# CACC
#    {'a': True,  'b': True, 'c': True},     # 1
#    {'a': True,  'b': True, 'c': False},    # 2
#    {'a': True,  'b': False, 'c': False},   # 4
#    {'a': False, 'b': False, 'c': False}    # 8

# CACC
#    {'a': True,  'b': True, 'c': False},    # 2
#    {'a': True,  'b': False, 'c': False},   # 4
#    {'a': False, 'b': False, 'c': True},    # 7
#    {'a': False, 'b': False, 'c': False}    # 8

# CACC
#    {'a': True,  'b': True, 'c': False},    # 2
#    {'a': True,  'b': False, 'c': False},   # 4
#    {'a': False, 'b': True,  'c': True},    # 5
#    {'a': False, 'b': False, 'c': False}    # 8


#######################33


# RACC
#    {'a': True,  'b': True, 'c': False},    # 2
#    {'a': True,  'b': False, 'c': False},   # 4
#    {'a': False, 'b': False, 'c': True},    # 7
#    {'a': False, 'b': False, 'c': False}    # 8


# RACC
#    {'a': True,  'b': True, 'c': True},     # 1
#    {'a': True,  'b': True, 'c': False},    # 2
#    {'a': True,  'b': False, 'c': False},   # 4
#    {'a': False, 'b': False, 'c': False}    # 8

#check_predicate_coverage(input_assignments)
#check_clause_coverage(input_assignments)
#check_racc(input_assignments)
check_cacc(input_assignments)
