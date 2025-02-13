-- Users table to store user information
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    settings JSONB -- Store user settings as JSON
);

-- Chat threads table to store conversation threads
CREATE TABLE chat_threads (
    thread_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    title VARCHAR(255),
    function_type VARCHAR(20) CHECK (function_type IN ('tutor', 'video', 'quiz')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP,
    model_type VARCHAR(20), -- gpt-4, gpt-3.5-turbo, claude-3
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Messages table to store chat messages
CREATE TABLE messages (
    message_id UUID PRIMARY KEY,
    thread_id UUID REFERENCES chat_threads(thread_id),
    user_id UUID REFERENCES users(user_id),
    content TEXT NOT NULL,
    is_user BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (thread_id) REFERENCES chat_threads(thread_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Documents table to store uploaded files
CREATE TABLE documents (
    document_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    thread_id UUID REFERENCES chat_threads(thread_id),
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_path VARCHAR(255),
    content_text TEXT, -- Extracted text content
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (thread_id) REFERENCES chat_threads(thread_id)
);

-- Videos table to store generated videos
CREATE TABLE videos (
    video_id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(document_id),
    user_id UUID REFERENCES users(user_id),
    title VARCHAR(255),
    duration INTEGER, -- in seconds
    video_url VARCHAR(255),
    thumbnail_url VARCHAR(255),
    transcript TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (document_id) REFERENCES documents(document_id)
);

-- Quizzes table to store generated quizzes
CREATE TABLE quizzes (
    quiz_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    document_id UUID REFERENCES documents(document_id),
    title VARCHAR(255),
    description TEXT,
    settings JSONB, -- Store quiz settings
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (document_id) REFERENCES documents(document_id)
);

-- Questions table to store quiz questions
CREATE TABLE questions (
    question_id UUID PRIMARY KEY,
    quiz_id UUID REFERENCES quizzes(quiz_id),
    question_text TEXT NOT NULL,
    question_type VARCHAR(20), -- multiple_choice, true_false, etc.
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id)
);

-- Options table to store question options
CREATE TABLE options (
    option_id UUID PRIMARY KEY,
    question_id UUID REFERENCES questions(question_id),
    option_text TEXT NOT NULL,
    is_correct BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id) REFERENCES questions(question_id)
);

-- Quiz attempts table to store user quiz attempts
CREATE TABLE quiz_attempts (
    attempt_id UUID PRIMARY KEY,
    quiz_id UUID REFERENCES quizzes(quiz_id),
    user_id UUID REFERENCES users(user_id),
    score INTEGER,
    total_questions INTEGER,
    completed_at TIMESTAMP,
    duration INTEGER, -- in seconds
    FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- User answers table to store answers for each attempt
CREATE TABLE user_answers (
    answer_id UUID PRIMARY KEY,
    attempt_id UUID REFERENCES quiz_attempts(attempt_id),
    question_id UUID REFERENCES questions(question_id),
    selected_option_id UUID REFERENCES options(option_id),
    is_correct BOOLEAN,
    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (attempt_id) REFERENCES quiz_attempts(attempt_id),
    FOREIGN KEY (question_id) REFERENCES questions(question_id),
    FOREIGN KEY (selected_option_id) REFERENCES options(option_id)
);

-- Indexes for better query performance
CREATE INDEX idx_chat_threads_user ON chat_threads(user_id);
CREATE INDEX idx_messages_thread ON messages(thread_id);
CREATE INDEX idx_documents_user ON documents(user_id);
CREATE INDEX idx_videos_user ON videos(user_id);
CREATE INDEX idx_quizzes_user ON quizzes(user_id);
CREATE INDEX idx_quiz_attempts_user ON quiz_attempts(user_id);