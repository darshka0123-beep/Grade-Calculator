from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Assignment:
    name: str
    earned_points: float
    possible_points: float

    @property
    def percentage(self) -> float:
        if self.possible_points == 0:
            return 0.0
        return (self.earned_points / self.possible_points) * 100.0

@dataclass 
class Category:
    name: str
    weight: float # Percentage out of 100 (e.g, 60 for 60%)
    assignments: List[Assignment] = field(default_factory=list)

    def add_assignment(self, name: str, earned: float, possible: float) -> None:
        if possible <= 0:
            raise ValueError("Possible points must be greater than zero.")
        self.assignments.append(Assignment(name, earned, possible)) 

    @property
    def current_average(self) -> Optional[float]:
     # Calculates the average percentage for this category based on total points.
     if not self.assignments:
         return None
     total_earned = sum(a.earned_points for a in self.assignments)
     total_possible = sum(a.possible_points for a in self.assignments)
     return (total_earned / total_possible) * 100.0

class Subject:
    def __init__(self, name:str):
        self.name = name
        self.categories: Dict[str, Category] = {}

    def add_category(self, name: str, weight: float) -> None:
        if weight < 0 or weight > 100:
            raise ValueError("Weight must be between 0 and 100.")
        self.categories[name] = Category(name, weight)

    def validate_weights(self) -> bool:
        # Returns True if category weights sum to 100%.
        total_weight = sum(cat.weight for cat in self.categories.values())
        return abs(total_weight - 100.0) < 1e-5

    def add_grade(self, category_name: str, assignment_name: str, earned: float, possible: float) -> None:
        if category_name not in self.categories:
            raise KeyError(f"Category '{category_name}' does not exist in {self.name}.")
        self.categories[category_name].add_assignment(assignment_name, earned, possible)

    def calculate_overall_grade(self) -> Dict[str, float]:
        # Calculates the subject's overall grade using active categories.
        # Re-weights active categories if some have no assignments yet. 

        active_weight_sum = 0.0
        weighted_score_sum = 0.0

        for cat in self.categories.values():
            avg = cat.current_average
            if avg is not None:
                active_weight_sum += cat.weight
                weighted_score_sum += (avg * (cat.weight / 100.0))

        if active_weight_sum == 0:
            return {"overall_percentage": 0.0, "effective_weight_evalutaed": 0.0}

        # Normalize score against the weight of currently evaluated categories
        normalized_grade = (weighted_score_sum / active_weight_sum) * 100.0
        return{
            "overall_percentage": round(normalized_grade, 2),
            "effective_weight_evaluated": round(active_weight_sum, 2)
        }

def calculate_required_final_score(self, target_overall:float, final_exam_weight:float) -> float:
    # Calculates required percentage on an upcoming final exam.
    current_data = self.calculate_overall_grade()
    current_grade = current_data["overall_percentage"]

    remaining_weight = 1.0 - (final_exam_weight / 100.0)
    required = (target_overall - (current_grade * remaining_weight)) / (final_exam_weight / 100.0)
    return round(required, 2)

class GradeManager:
    def __init__(self):
        self.subjects: Dict[str, Subject] = {}

    def add_subject(self, name:str) -> Subject:
        subject = Subject(name)
        self.subjects[name] = subject
        return subject

    def get_subject(self, name:str) -> Optional[Subject]:
        return self.subjects.get(name)

    def calculate_gpa(self, grade_scale: Optional[Dict[str, float]] = None) -> float:
        # Calculates an unweighted GPA across all tracked subjects.
        if not self.subjects:
            return 0.0

        if grade_scale is None:
            # Standard 4.0 scale mapping
            grade_scale = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "F": 0.0}

        total_points = 0.0
        count = 0

        for subject in self. subjects.values():
            percentage = subject.calculate_overall_grade()["overall_percentage"]
            letter = self.percentage_to_letter(percentage)
            total_points += grade_scale.get(letter, 0.0)
            count += 1

        return round(total_points / count, 2) if count > 0 else 0.0
    @staticmethod
    def percentage_to_letter(percentage: float) -> str:
        if percentage >= 90.0:
            return "A"
        elif percentage >= 80.0:
            return "B"
        elif percentage >= 70.0:
            return "C"
        elif percentage >= 60.0:
            return "D"
        else: 
            return "F"

# ----------------------------------------------------------------------------------------
# Example Usage
# ----------------------------------------------------------------------------------------

if __name__ == "__main__":
    manager = GradeManager()

    # 1. Setup AP Calculus BC
    calc = manager.add_subject("AP Calculus BC")
    calc.add_category("Tests", 60.0)
    calc.add_category("Quizzes", 25.0)
    calc.add_category("Homework", 15.0)

    # Populate Grades
    calc.add_grade("Tests", "Unit 1 Exam", 52, 100) # Failed Test
    calc.add_grade("Tests", "Unit 2 Exam", 88, 100) # Recovery Test
    calc.add_grade("Quizzes", "Derivatives Quiz", 18, 20)
    calc.add_grade("Homework", "Problem Set 1", 10, 20)

    # Setup Chem H
    chem = manager.add_subject("Chem H")
    chem.add_category("Exams", 70.0)
    chem.add_category("Labs", 30.0)

    chem.add_grade("Exams", "Kinematics Test", 85, 100)
    chem.add_grade("Labs", "Vector Analysis Lab", 28, 30)

    # Output Single Subject Analysis
    print("---Multi-Subject Summary ---")
    for name, subj in manager.subjects.items():
        score = subj.calculate_overall_grade()["overall_percentage"]
        letter = GradeManager.percentage_to_letter(score)
        print(f"{name}: {score}% ({letter})")

    print(f"\nCalculated GPA: {manager.calculate_gpa()}")




        

