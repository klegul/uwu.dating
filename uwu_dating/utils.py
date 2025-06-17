from uwu_dating.db import get_user_answers, count_questions
from uwu_dating.model import User


def get_user_score(self_user: User, other_user: User) -> float:
    self_answers = get_user_answers(self_user.id)
    other_answers = get_user_answers(other_user.id)

    points = 0
    for self_answer in self_answers:
        for other_answer in other_answers:
            if self_answer.question_number == other_answer.question_number:
                if self_answer.answer == other_answer.answer:
                    points += 1
                break

    return float(points) / float(count_questions())