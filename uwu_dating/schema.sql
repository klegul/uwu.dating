DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS question;
DROP TABLE IF EXISTS answer_choice;
DROP TABLE IF EXISTS user_answer;
DROP TABLE IF EXISTS poke;
DROP TABLE IF EXISTS message;

CREATE TABLE user (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    dect TEXT,
    meeting_point TEXT
);

CREATE TABLE question (
    number INTEGER PRIMARY KEY,
    question TEXT NOT NULL,
    type TEXT NOT NULL,
    submit_label TEXT NOT NULL
);

CREATE TABLE answer_choice (
    question_number INTEGER NOT NULL REFERENCES question(number),
    number INTEGER NOT NULL,
    answer TEXT NOT NULL,
    PRIMARY KEY (question_number, number)
);

CREATE TABLE user_answer (
    user_id TEXT NOT NULL REFERENCES user(id),
    question_number INTEGER NOT NULL REFERENCES question(number),
    answer TEXT NOT NULL
);

CREATE TABLE poke (
    id TEXT PRIMARY KEY,
    poker_id TEXT NOT NULL REFERENCES user(id),
    poked_id TEXT NOT NULL REFERENCES user(id),
    acked INTEGER NOT NULL
);

CREATE TABLE message (
    id TEXT PRIMARY KEY ,
    sender_id TEXT NOT NULL REFERENCES user(id),
    recipient_id TEXT NOT NULL REFERENCES user(id),
    content TEXT NOT NULL,
    timestamp INTEGER NOT NULL
)