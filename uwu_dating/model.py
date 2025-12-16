from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: str
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
    user_id: str
    answer: str

@dataclass(frozen=True)
class Poke:
    id: str
    poker_id: str
    poked_id: str
    acked: bool

@dataclass(frozen=True)
class Message:
    id: str
    sender_id: str
    recipient_id: str
    content: str
    timestamp: int