from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: int
    name: str
    dect: str
    meeting_point: str


@dataclass(frozen=True)
class Question:
    number: int
    question: str
    type: str
    submit_label: str


@dataclass(frozen=True)
class AnswerChoice:
    question_number: int
    number: int
    answer: str


@dataclass(frozen=True)
class UserAnswer:
    question_number: int
    user_id: int
    answer: str
