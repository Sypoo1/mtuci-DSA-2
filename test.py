import json

class Teacher:
    def __init__(self, name, gender, faculty, department, years_experience, associate_professor, assistant, department_head, head_campus, module):
        self.name = name
        self.gender = gender
        self.faculty = faculty
        self.department = department
        self.years_experience = years_experience
        self.associate_professor = associate_professor
        self.assistant = assistant
        self.department_head = department_head
        self.head_campus = head_campus
        self.module = module

    def to_dict(self):
        return {
            "name": self.name,
            "gender": self.gender,
            "faculty": self.faculty,
            "department": self.department,
            "years_experience": self.years_experience,
            "associate_professor": self.associate_professor,
            "assistant": self.assistant,
            "department_head": self.department_head,
            "head_campus": self.head_campus,
            "module": self.module
        }

    @staticmethod
    def from_dict(data):
        return Teacher(
            name=data["name"],
            gender=data["gender"],
            faculty=data["faculty"],
            department=data["department"],
            years_experience=data["years_experience"],
            associate_professor=data["associate_professor"],
            assistant=data["assistant"],
            department_head=data["department_head"],
            head_campus=data["head_campus"],
            module=data["module"]
        )


DATA_FILE = "teachers.json"


def load_teachers():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [Teacher.from_dict(entry) for entry in data["teachers"]]


def save_teachers(teachers):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"teachers": [teacher.to_dict() for teacher in teachers]}, f, ensure_ascii=False, indent=4)


questions = [
    ("Is the teacher male or female?", "gender", ["Male", "Female"]),
    ("Which faculty does the teacher belong to?", "faculty", [
        "Information Technology",
        "Cybernetics and Information Security"
    ]),
    ("Which department does the teacher belong to?", "department", [
        "Mathematical Cybernetics and IT",
        "Corporate Information Systems",
        "Mathematical Analysis",
        "Probability and Applied Mathematics",
        "Physical Education"
    ]),
    ("Does the teacher have more than 10 years of experience?", "years_experience", 10),
    ("Is the teacher an Associate Professor?", "associate_professor", True),
    ("Is the teacher an Assistant?", "assistant", True),
    ("Is the teacher the head of the department?", "department_head", True),
    ("Which campus is the teacher located at?", "head_campus", ["Narodnoe Opolchenie", "Aviamatornaya", "Both"]),
    ("Which module does the teacher teach?", "module", [
        "Information Technology and Programming",
        "Structure and Algorithms for Data Processing",
        "Practical Project",
        "Discrete Mathematics",
        "Higher Mathematics",
        "Mathematical Methods in Big Data",
        "Probability and Statistics",
        "Sport",
        "Databases"
    ])
]

def ask_question(question):
    print(question[0])
    if isinstance(question[2], list):
        for i, option in enumerate(question[2]):
            print(f"{i + 1}. {option}")
        while True:
            try:
                answer = int(input("Enter the number corresponding to your answer: "))
                if 1 <= answer <= len(question[2]):
                    return question[2][answer - 1]
            except ValueError:
                print("Invalid input. Please enter a valid number.")
    else:
        while True:
            answer = input("Enter 'Yes' or 'No': ").lower()
            if answer in ["yes", "no"]:
                return answer == "yes"

def play_game():
    teachers = load_teachers()
    possible_teachers = teachers[:]
    user_answers = {}

    for question in questions:
        answer = ask_question(question)
        attribute = question[1]
        user_answers[attribute] = answer

        if isinstance(question[2], int):  
            if answer:
                possible_teachers = [t for t in possible_teachers if getattr(t, attribute) >= question[2]]
            else:
                possible_teachers = [t for t in possible_teachers if getattr(t, attribute) < question[2]]
        else:
            possible_teachers = [t for t in possible_teachers if getattr(t, attribute) == answer]

        if len(possible_teachers) == 0:
            print("No matching teacher found. You can add this teacher.")
            add_teacher(user_answers)
            return

    if len(possible_teachers) == 1:
        print(f"The teacher you're thinking of is: {possible_teachers[0].name}")
    else:
        print("Multiple possible teachers found:")
        for teacher in possible_teachers:
            print(teacher.name)

def add_teacher(user_answers):
    name = input("Enter the teacher's name: ")
    years_experience = int(input("Enter the teacher's years of experience: "))

    new_teacher = Teacher(
        name=name,
        gender=user_answers.get("gender", "Unknown"),
        faculty=user_answers.get("faculty", "Unknown"),
        department=user_answers.get("department", "Unknown"),
        years_experience=years_experience,
        associate_professor=user_answers.get("associate_professor", False),
        assistant=user_answers.get("assistant", False),
        department_head=user_answers.get("department_head", False),
        head_campus=user_answers.get("head_campus", "Unknown"),
        module=user_answers.get("module", "None")
    )

    teachers = load_teachers()
    teachers.append(new_teacher)
    save_teachers(teachers)
    print(f"Teacher '{name}' added to the database!")

if __name__ == "__main__":
    play_game()

