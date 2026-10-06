import streamlit as st
import pandas as pd

st.set_page_config(page_title="Exact Grade & Recovery Calculator", page_icon="🧮", layout="wide")

st.title("🧮 Exact Grade & Recovery Calculator")
st.write("Track exact percentage averages per subject with custom category weights, simulate future tests, and find target scores.")

# Initialize session state for multi-subject storage
if "courses" not in st.session_state:
    st.session_state.courses = {}

# _____________________________________________________________________________________________________________________________________________________________________
# Helper: Percentage to 4.0 GPA Conversion
#_________________________________________________________________________________________________________________________________________________________________________

def pct_to_gpa(pct):
    if pct is None:
        return 0.0
    if pct >= 93.0: return 4.0
    elif pct >= 90.0: return 3.7
    elif pct >= 87.0: return 3.3
    elif pct >= 83.0: return 3.0
    elif pct >= 80.0: return 2.7
    elif pct >= 77.0: return 2.3
    elif pct >= 73.0: return 2.0
    elif pct >= 70.0: return 1.7
    elif pct >= 67.0: return 1.3
    elif pct >= 65.0: return 1.0
    else: return 0.0

# ________________________________________________________________________________________________________________________________________________________
# Sidebar: Add and manage subjects
#___________________________________________________________________________________________________________________________________________________________
st.sidebar.header("Manage Subjects")
new_course = st.sidebar.text_input("Add New Subject Name:", placeholder="e.g. AP Calculus BC")
course_credits = st.sidebar.number_input("Course Credits:", min_value=0.5, max_value=6.0, value=3.0, step=0.5)

if st.sidebar.button("Add Subject") and new_course:
    if new_course not in st.session_state.courses:
        st.session_state.courses[new_course] = {
            "credits": course_credits,
            "categories": {}, # {category_name: weight_percent}
            "assignments": [] # list of dicts: {name, category, earned, possible}
        }
        st.sidebar.success(f"Added {new_course}")
        st.rerun()
    else:
        st.sidebar.warning("Subject already exists.")

if st.session_state.courses:
    total_quality_points = 0.0
    total_active_credits = 0.0

    for course_name, course_info in st.session_state.courses.items():
        cat_totals = {c: {"earned": 0.0, "possible": 0.0} for c in course_info["categories"]}
        for a in course_info["assignments"]:
            if a["category"] in cat_totals:
                cat_totals[a["category"]]["earned"] += a["earned"]
                cat_totals[a["category"]]["possible"] += a["possible"]

        active_weight = 0.0
        weighted_sum = 0.0
        for c_name, c_w in course_info["categories"].items():
            if cat_totals[c_name]["possible"] > 0:
                cat_pct = (cat_totals[c_name]["earned"] / cat_totals[c_name]["possible"]) * 100.0
                active_weight += c_w
                weighted_sum += cat_pct * (c_w / 100.0)

        if active_weight > 0:
            course_avg = weighted_sum / (active_weight / 100.0)
            gpa_points = pct_to_gpa(course_avg)
            credits = course_info.get("credits", 3.0)

            total_quality_points += gpa_points * credits
            total_active_credits += credits

    if total_active_credits > 0:
        cumulative_gpa = total_quality_points / total_active_credits
        st.sidebar.markdown("---")
        st.sidebar.metric("Cumulative Unweighted GPA", f"{cumulative_gpa:.2f} / 4.00")

if not st.session_state.courses:
    st.info("Add a subject in the sidebar to get started!")
    st.stop()

selected_course = st.sidebar.selectbox("Select Subject to View/Edit", list(st.session_state.courses.keys()))
course_data = st.session_state.courses[selected_course]

st.header(f"Subject: {selected_course}")

#_________________________________________________________________________________________________________________________________________________________
# Section 1: Define Category Weights
#____________________________________________________________________________________________________________________________________________________________________
st.subheader("1. Category Weights Setup")
st.caption("Define the categories for this specific class and their percentage weights (must total 100%).")

col_cat1, col_cat2, col_cat3 = st.columns([2, 2, 1])
with col_cat1:
    cat_name_input = st.text_input("Category Name:", placeholder="e.g. Tests", key="cat_name")
with col_cat2:
    cat_weight_input = st.number_input("Category Weight (%):", min_value=0.1, max_value=100.0, value=50.0, step=1.0, key="cat_weight")
with col_cat3:
    st.write("")
    st.write("")
    if st.button("Add Category") and cat_name_input:
        course_data["categories"][cat_name_input] = cat_weight_input
        st.success(f"Added {cat_name_input}({cat_weight_input:.2f}%)")
        st.rerun()

# Display active categories and weight total
if course_data["categories"]:
    total_w = sum(course_data["categories"].values())
    cat_summary = ", ".join([f"**{k}**: {v:.2f}%" for k, v in course_data["categories"].items()])
    st.markdown(f"**Current Categories:** {cat_summary}")

    if abs(total_w - 100.0) > 1e-4:
        st.warning(f"Total category weights currently dum to **{total_w:.2f}%** (Should equal 100.00%).")
else: 
        st.info("No categories added yet. Add your class categories above.")
st.divider()

#______________________________________________________________________________________________________________________________________________________
# Section 2: Add Grades & calculate Exact Average
#___________________________________________________________________________________________________________________________________________________________
st. subheader("2. Add Grades & Calculate Exact Average")

if course_data["categories"]:
    # Calculate catgeory totals before column display
    cat_totals = {c: {"earned": 0.0, "possible": 0.0} for c in course_data["categories"]}
    for a in course_data["assignments"]:
        c = a["category"]
        if c in cat_totals:
            cat_totals[c]["earned"] += a["earned"]
            cat_totals[c]["possible"] += a["possible"]
    col_g1, col_g2 = st.columns([1,1])

    with col_g1:
        st.write("### Log an Assignment")
        with st.form("add_assignment_form", clear_on_submit=True):
            assign_name = st.text_input("Assignment Name:", placeholder="Unit 2 Test")
            assign_cat = st.selectbox("Category:", list(course_data["categories"].keys()))
            earned_pts = st.number_input("Points Earned:", min_value=0.0, value=85.0, step=0.5)
            possible_pts = st.number_input("Points Possible:", min_value=0.1, value=100.0, step=0.5)

            if st.form_submit_button("Add Grade"):
                if assign_name:
                    course_data["assignments"].append({
                        "name": assign_name,
                        "category": assign_cat,
                        "earned": earned_pts,
                        "possible": possible_pts
                    })
                    st.success(f"Logged {assign_name}")
                    st.rerun()

    active_weight_sum = 0.0
    weighted_score_sum = 0.0

    with col_g2:
        st.write("### Category & Overall Breakdown")

        for c_name, c_weight in course_data["categories"].items():
            earned = cat_totals[c_name]["earned"]
            possible = cat_totals[c_name]["possible"]

            if possible > 0:
                cat_pct = (earned / possible) * 100.0
                active_weight_sum += c_weight
                weighted_score_sum += (cat_pct * (c_weight / 100.0))
                st.write(f"• **{c_name}** ({c_weight:.2f}% weight): **{cat_pct:.2f}%** ({earned:.1f}/{possible:.1f})")
            else:
                st.write(f"• **{c_name}** ({c_weight:.2f}% weight): *No grades logged yet*")

        if active_weight_sum > 0:
            current_exact_avg = (weighted_score_sum / (active_weight_sum / 100.0))
            st.metric("Current Class Average", f"{current_exact_avg:.2f}%")
        else:
            current_exact_avg = None
            st.info("Log at least one assignment to see your exact average.")

    # Show logged assignments Table
    if course_data["assignments"]:
        st.write("### Logged Assignments")
        df_assignments = pd.DataFrame(course_data["assignments"])
        df_assignments["Percentage"] = (df_assignments["earned"] / df_assignments["possible"] * 100).round(2)

        st.dataframe(df_assignments, use_container_width=True)

        if st.button("Clear All Assignents for Subject"):
            course_data["assignments"] = []
            st.rerun()

else:
    current_exact_avg = None
    st.info("Please set up your category weights first in Section 1.")

st.divider()
# Section 3: Next Test & Target Score Calculator
st.subheader("3. Advanced Grade Analytics & Target Goal Finder")

if current_exact_avg is not None:
    tab_goal, tab_bounds, tab_sim = st.tabs([
        "Letter Grade Goal Finder",
        "Best/Worst Case Bounds",
        "Multi-Assignment Simulator",
    ])

    #_________________________________________________________________________________________________________________________________________________________________________________
    # Tab: 1 Target Score Calculator based on Letter Grade
    #_________________________________________________________________________________________________________________________________________________________________________________________
    with tab_goal:
        st.write("Determine the exact grade required on an upcoming assignment to hit a target **Letter Grade**.")

        col_t1, col_t2, col_t3 = st.columns([1,1,1])
        with col_t1:
            target_cat = st.selectbox("Upcoming Category:", list(course_data["categories"].keys()), key="goal_cat")
        with col_t2:
            grade_cutoffs = {"A (93%)": 93.0, "A- (90%)": 90.0, "B+ (87%)": 87.0, "B (83%)": 83.0, "B- (80%)": 80.0, "C+ (77%)": 77.0, "C(73%)": 73.0}
            selected_grade = st.selectbox("Target Letter Grade:", list(grade_cutoffs.keys()))
            target_overall = grade_cutoffs[selected_grade]
        with col_t3:
            next_possible_pts = st.number_input("Upcoming Test Possible Points:", min_value=1.0, value=100.0, step=5.0, key="goal_poss")

        if st.button("Calculate Target Score", type="primary"):
            c_earned = cat_totals[target_cat]["earned"]
            c_possible = cat_totals[target_cat]["possible"]
            c_weight = course_data["categories"][target_cat]

            other_weighted_sum = sum(
                (cat_totals[c]["earned"] / cat_totals[c]["possible"] * 100.0) * (w / 100.0)
                for c, w in course_data["categories"].items()
                if c != target_cat and cat_totals[c]["possible"] > 0
            )

            # Weight factor calculation
            required_cat_pct = ((target_overall * (active_weight_sum / 100.0)) - other_weighted_sum) / (c_weight / 100.0)
            required_earned_pts = (required_cat_pct / 100.0) * (c_possible + next_possible_pts) - c_earned
            required_test_pct = (required_earned_pts / next_possible_pts) * 100.0

            st.markdown("---")
            col_res1, col_res2 = st.columns([1,2])
            with col_res1:
                st.metric("Required Score", f"{required_earned_pts:.1f} / {next_possible_pts:.0f}", f"{required_test_pct:.1f}%")
            with col_res2:
                if required_test_pct > 100.0:
                    st.error(f"You need **{required_test_pct:.1f}%** to reach a **{selected_grade}**. You will need extra credit!")
                elif required_test_pct <= 0:
                    st.success(f"You have already secured a **{selected_grade}**! A 0% on this test will keep you above target.")
                else:
                    st.info(f"Score **{required_earned_pts:.1f} pts** ({required_test_pct:.1f}%) or higher to secure a **{selected_grade}**.")
#___________________________________________________________________________________________________________________________________________________________________
# Tab 2: Best & Worst Case Scenarios
#____________________________________________________________________________________________________________________________________________________________________________
with tab_bounds:
    st.write("Calculate the maximum possible grade floor and ceiling given upcoming total assignment weights.")

    future_pts = st.number_input("Total Remaining Points to be Graded in Class:", min_value=1.0, value=100.0, step=10.0)
    bound_cat = st.selectbox("Category for Remaining Points:", list(course_data["categories"].keys()), key="bound_cat")

    if st.button("Calculate Grade Boundaries"):
        # Best Case Scenario (100% on remaining)
        best_totals = {c: {"earned": cat_totals[c]["earned"], "possible": cat_totals[c]["possible"]} for c in cat_totals}
        best_totals[bound_cat]["earned"] += future_pts
        best_totals[bound_cat]["possible"] += future_pts

        best_w_sum = sum((best_totals[c]["earned"] / best_totals[c]["possible"] * 100.0) * (w / 100.0) for c, w in course_data["categories"].items() if best_totals[c]["possible"] > 0)
        best_avg = best_w_sum / (active_weight_sum / 100.0)

        # Worst Case Scenario (0%  on remaining)
        worst_totals = {c: {"earned": cat_totals[c]["earned"], "possible": cat_totals[c]["possible"]} for c in cat_totals}
        worst_totals[bound_cat]["possible"] += future_pts

        worst_w_sum = sum((worst_totals[c]["earned"] / worst_totals[c]["possible"] * 100.0) * (w / 100.0) for c, w in course_data["categories"].items() if best_totals[c]["possible"] > 0)
        worst_avg = worst_w_sum / (active_weight / 100.0)

        st.markdown("---")
        b_col1, b_col2, b_col3 = st.columns(3)
        b_col1.metric("Current Average", f"{current_exact_avg:.2f}%")
        b_col2.metric("Worst Case Floor (0%)", f"{worst_avg:.2f}%", f"{worst_avg - current_exact_avg:.2f}%")
        b_col3.metric("Best Case Ceiling (100%)", f"{best_avg:.2f}%", f"+{best_avg - current_exact_avg:.2f}%")

        st.caption("Grade Range Potential:")
        st.progress(min(max(int(best_avg), 0), 100))
#________________________________________________________________________________________________________________________________________________________________________________________________________________________
# Tab 3: Single Test Quick Simulator:
#____________________________________________________________________________________________________________________________________________________________________________________________________________________________________-
with tab_sim:
    st.write("Test how a custom grade entry impacts your overall standing before logging it.")
    sim_col1, sim_col2, sim_col3 = st.columns(3)

    with sim_col1:
        sim_cat = st.selectbox("Category:", list(course_data["categories"].keys()), key="sim_c")
    with sim_col2:
        sim_earned = st.number_input("Hypothetical Points Earned:", min_value=0.0, value=88.0, step=1.0)
    with sim_col3:
        sim_possible = st.number_input("Hypothetical Total Points:", min_value=1.0, value=100.0, step=1.0)

    if st.button("Run Simulation"):
        temp_totals = {c: {"earned": cat_totals[c]["earned"], "possible": cat_totals[c]['possible']} for c in cat_totals}
        temp_totals[sim_cat]["earned"] += sim_earned
        temp_totals[sim_cat]["possible"] += sim_possible

        sim_weighted_sum = sum((temp_totals[c]["earned"] / temp_totals[c]["possible"] * 100.0) * (w / 100.0) for c, w in course_data["categories"].items() if temp_totals[c]["possible"] > 0)
        sim_final_avg = sim_weighted_sum / (active_weight_sum / 100.0)
        diff = sim_final_avg - current_exact_avg

        if diff >= 0:
            st.success(f"Simualted Class Average: **{sim_final_avg:.2f}%** (+{diff:.2f})")
        else:
            st.error(f"Simulated Class Average: **{sim_final_avg:.2f}%** ({diff:.2f}% change)")
    else:
        st.info("Log at least one assignment in Section 2 to unlock analytics and target calculators.")