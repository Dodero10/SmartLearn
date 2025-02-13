import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import TimerIcon from '@mui/icons-material/Timer';

const QuizContainer = styled.div`
  display: flex;
  height: 100%;
`;

const QuizSection = styled.div`
  flex: 1;
  height: 100%;
  padding: 24px;
  overflow-y: auto;
  border-right: 1px solid #e0e0e0;
`;

const QuizHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

const Timer = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: ${props => props.timeWarning ? '#fff3e0' : '#f0f2ff'};
  color: ${props => props.timeWarning ? '#e65100' : '#1a237e'};
  border-radius: 20px;
  font-weight: 500;
`;

const QuestionCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`;

const QuestionHeader = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
`;

const QuestionNumber = styled.div`
  font-weight: 500;
  color: #1a237e;
`;

const Question = styled.div`
  font-size: 18px;
  margin-bottom: 24px;
  line-height: 1.6;
`;

const OptionsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const Option = styled.div`
  padding: 16px;
  border: 2px solid ${props => {
    if (props.showResults) {
      if (props.isCorrect) return '#4caf50';
      if (props.isSelected && !props.isCorrect) return '#f44336';
    }
    return props.isSelected ? '#1a237e' : '#e0e0e0';
  }};
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: ${props => {
    if (props.showResults) {
      if (props.isCorrect) return '#e8f5e9';
      if (props.isSelected && !props.isCorrect) return '#ffebee';
    }
    return props.isSelected ? '#f0f2ff' : 'white';
  }};

  &:hover {
    background: ${props => props.showResults ? 'none' : '#f0f2ff'};
    border-color: ${props => props.showResults ? 'none' : '#1a237e'};
  }
`;

const ResultIcon = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  color: ${props => props.correct ? '#4caf50' : '#f44336'};
  margin-top: 16px;
  font-weight: 500;
`;

const ButtonContainer = styled.div`
  display: flex;
  justify-content: space-between;
  margin-top: 32px;
`;

const Button = styled.button`
  padding: 12px 24px;
  border-radius: 8px;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  background: ${props => props.primary ? '#1a237e' : '#f0f2ff'};
  color: ${props => props.primary ? 'white' : '#1a237e'};

  &:hover {
    background: ${props => props.primary ? '#0e1859' : '#e3e7ff'};
  }

  &:disabled {
    background: #e0e0e0;
    color: #9e9e9e;
    cursor: not-allowed;
  }
`;

const QuizInterface = ({ quiz, settings, onComplete }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(settings.timePerQuestion * quiz.questions.length);
  const [showResults, setShowResults] = useState(false);
  const [score, setScore] = useState(0);

  useEffect(() => {
    if (timeLeft > 0 && !showResults) {
      const timer = setInterval(() => {
        setTimeLeft(prev => prev - 1);
      }, 1000);
      return () => clearInterval(timer);
    } else if (timeLeft === 0 && !showResults) {
      handleSubmit();
    }
  }, [timeLeft, showResults]);

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const handleOptionSelect = (questionIndex, optionIndex) => {
    if (showResults) return;
    setSelectedAnswers(prev => ({
      ...prev,
      [questionIndex]: optionIndex
    }));
  };

  const handleSubmit = () => {
    let correctAnswers = 0;
    quiz.questions.forEach((question, index) => {
      if (selectedAnswers[index] === question.correctAnswer) {
        correctAnswers++;
      }
    });
    setScore(correctAnswers);
    setShowResults(true);
    onComplete && onComplete({
      score: correctAnswers,
      total: quiz.questions.length,
      answers: selectedAnswers
    });
  };

  return (
    <QuizContainer>
      <QuizSection>
        <QuizHeader>
          <h2>Quiz</h2>
          <Timer timeWarning={timeLeft < 60}>
            <TimerIcon />
            {formatTime(timeLeft)}
          </Timer>
        </QuizHeader>
        
        {quiz.questions.map((question, qIndex) => (
          <QuestionCard key={qIndex}>
            <QuestionHeader>
              <QuestionNumber>Question {qIndex + 1}</QuestionNumber>
            </QuestionHeader>
            <Question>{question.question}</Question>
            <OptionsList>
              {question.options.map((option, oIndex) => (
                <Option
                  key={oIndex}
                  isSelected={selectedAnswers[qIndex] === oIndex}
                  onClick={() => handleOptionSelect(qIndex, oIndex)}
                  showResults={showResults}
                  isCorrect={showResults && oIndex === question.correctAnswer}
                >
                  {option}
                  {showResults && selectedAnswers[qIndex] === oIndex && (
                    <ResultIcon correct={oIndex === question.correctAnswer}>
                      {oIndex === question.correctAnswer ? (
                        <>
                          <CheckCircleIcon />
                          Correct
                        </>
                      ) : (
                        <>
                          <CancelIcon />
                          Incorrect
                        </>
                      )}
                    </ResultIcon>
                  )}
                </Option>
              ))}
            </OptionsList>
            {showResults && question.explanation && (
              <div style={{ marginTop: '16px', color: '#666' }}>
                <strong>Explanation:</strong> {question.explanation}
              </div>
            )}
          </QuestionCard>
        ))}

        <ButtonContainer>
          {!showResults ? (
            <Button 
              primary 
              onClick={handleSubmit}
              disabled={Object.keys(selectedAnswers).length < quiz.questions.length}
            >
              Submit Quiz
            </Button>
          ) : (
            <div>
              <h3>Final Score: {score}/{quiz.questions.length}</h3>
            </div>
          )}
        </ButtonContainer>
      </QuizSection>
    </QuizContainer>
  );
};

export default QuizInterface; 