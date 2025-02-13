import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { chatService } from '../../services/chatService';
import { functionService } from '../../services/functionService';
import ChatMessage from './ChatMessage';
import { v4 as uuidv4 } from 'uuid';
import SendIcon from '@mui/icons-material/Send';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import QuizIcon from '@mui/icons-material/Quiz';
import VideoLibraryIcon from '@mui/icons-material/VideoLibrary';
import SchoolIcon from '@mui/icons-material/School';
import HelpIcon from '@mui/icons-material/Help';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import VideoPlayer from '../video/VideoPlayer';
import QuizInterface from '../quiz/QuizInterface';

const ChatContainer = styled.div`
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
`;

const Header = styled.div`
  padding: 16px 24px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const HeaderLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const HeaderTitle = styled.h2`
  margin: 0;
  color: #1a237e;
  font-size: 1.25rem;
`;

const ModelSelector = styled.div`
  position: relative;
`;

const ModelButton = styled.button`
  background: none;
  border: 1px solid #e0e0e0;
  padding: 8px 12px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #1a237e;
  font-size: 14px;
  transition: all 0.3s ease;

  &:hover {
    background: #f0f2ff;
    border-color: #1a237e;
  }
`;

const ModelDropdown = styled.div`
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 4px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
  min-width: 200px;
  display: ${props => props.isOpen ? 'block' : 'none'};
`;

const ModelOption = styled.div`
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.3s ease;
  color: ${props => props.active ? '#1a237e' : '#333'};
  background: ${props => props.active ? '#f0f2ff' : 'transparent'};
  font-weight: ${props => props.active ? '500' : 'normal'};

  &:hover {
    background: #f0f2ff;
  }

  &:first-child {
    border-radius: 8px 8px 0 0;
  }

  &:last-child {
    border-radius: 0 0 8px 8px;
  }
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background-color: #f8f9fa;
  display: flex;
  flex-direction: column;
  gap: 24px;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 3px;
  }
`;

const InputWrapper = styled.div`
  border-top: 1px solid #e0e0e0;
  padding: 24px;
  background: white;
`;

const InputContainer = styled.div`
  max-width: 768px;
  margin: 0 auto;
  position: relative;
  display: flex;
  align-items: flex-end;
  gap: 12px;
`;

const TextArea = styled.textarea`
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  line-height: 1.5;
  resize: none;
  height: 56px;
  max-height: 200px;
  overflow-y: auto;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: #1a237e;
    box-shadow: 0 0 0 2px rgba(26, 35, 126, 0.1);
  }
`;

const IconButton = styled.button`
  background: none;
  border: none;
  padding: 8px;
  cursor: pointer;
  color: ${props => props.disabled ? '#9e9e9e' : '#1a237e'};
  transition: all 0.3s ease;
  border-radius: 4px;

  &:hover:not(:disabled) {
    background: rgba(26, 35, 126, 0.1);
  }

  &:disabled {
    cursor: not-allowed;
  }
`;

const FileInput = styled.input`
  display: none;
`;

const WelcomeMessage = styled.div`
  text-align: center;
  color: #666;
  margin: 48px 0;

  h1 {
    color: #1a237e;
    margin-bottom: 16px;
  }

  p {
    font-size: 1.1rem;
    max-width: 600px;
    margin: 0 auto;
  }
`;

const FunctionBar = styled.div`
  padding: 12px 24px;
  background: #f8f9fa;
  border-top: 1px solid #e0e0e0;
`;

const FunctionContainer = styled.div`
  max-width: 768px;
  margin: 0 auto;
  display: flex;
  gap: 12px;
`;

const FunctionButton = styled.button`
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  border: 1px solid ${props => props.active ? '#1a237e' : '#e0e0e0'};
  border-radius: 8px;
  background: ${props => props.active ? '#f0f2ff' : 'white'};
  color: ${props => props.active ? '#1a237e' : '#666'};
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;

  &:hover {
    background: #f0f2ff;
    border-color: #1a237e;
    color: #1a237e;
  }

  svg {
    font-size: 20px;
  }
`;

const InfoText = styled.div`
  text-align: center;
  color: #666;
  font-size: 14px;
  margin-top: 8px;
`;

const VideoModeContainer = styled.div`
  display: flex;
  height: 100%;
`;

const VideoSection = styled.div`
  flex: 1;
  height: 100%;
  border-right: 1px solid #e0e0e0;
`;

const ChatSection = styled.div`
  width: 350px;
  height: 100%;
  display: flex;
  flex-direction: column;
`;

/**
 * Component chính xử lý giao diện chat
 * Bao gồm:
 * - Hiển thị danh sách tin nhắn
 * - Ô nhập tin nhắn
 * - Nút gửi tin nhắn
 * - Xử lý gửi/nhận tin nhắn với backend
 */
const ChatBox = React.forwardRef(({ 
  onNewChat, 
  activeChatId, 
  activeFunction, 
  onFunctionChange, 
  settings,
  chatHistory 
}, ref) => {
  // State lưu trữ danh sách tin nhắn
  const [messages, setMessages] = useState([]);
  // State lưu trữ nội dung đang nhập
  const [input, setInput] = useState('');
  // State đánh dấu đang gửi tin nhắn
  const [isLoading, setIsLoading] = useState(false);
  // Ref để scroll đến tin nhắn cuối cùng
  const messagesEndRef = useRef(null);
  // ID phiên chat
  const threadId = useRef(activeChatId || uuidv4());
  // Ref lưu nội dung tin nhắn đang stream
  const streamedMessageRef = useRef('');
  const fileInputRef = useRef(null);
  const [selectedModel, setSelectedModel] = useState('gpt-4');
  const [isModelDropdownOpen, setIsModelDropdownOpen] = useState(false);
  const [videoId, setVideoId] = useState(null);
  const [transcript, setTranscript] = useState(null);
  const [quizData, setQuizData] = useState(null);
  const [showQuizInterface, setShowQuizInterface] = useState(false);
  const [showVideoInterface, setShowVideoInterface] = useState(false);
  const uploadedFile = useRef(null);
  
  // Kiểm tra xem cuộc hội thoại đã bắt đầu chưa
  const hasStartedChat = messages.length > 0;

  const models = [
    { id: 'gpt-4', name: 'GPT-4' },
    { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo' },
    { id: 'claude-3', name: 'Claude 3' },
  ];

  const handleModelSelect = (modelId) => {
    setSelectedModel(modelId);
    setIsModelDropdownOpen(false);
  };

  useEffect(() => {
    if (activeChatId) {
      // TODO: Load messages for the active chat
    } else {
      setMessages([]);
    }
  }, [activeChatId]);

  const handleInputChange = (e) => {
    setInput(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 200)}px`;
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    uploadedFile.current = file;
    
    let message = '';
    setIsLoading(true);
    
    switch (activeFunction) {
      case 'video':
        message = `Slides "${file.name}" has been uploaded. Please provide any specific instructions for the video conversion.`;
        setMessages(prev => [...prev, { 
          text: message, 
          isUser: false 
        }]);
        break;

      case 'quiz':
        message = `Generating quiz from ${file.name}...`;
        try {
          setMessages(prev => [...prev, { text: message, isUser: true, isFileUpload: true }]);
          const quiz = await functionService.generateQuiz(file);
          setMessages(prev => [...prev, { 
            text: '### Generated Quiz\n\n' + formatQuiz(quiz),
            isUser: false 
          }]);
        } catch (error) {
          setMessages(prev => [...prev, { 
            text: 'Sorry, I encountered an error generating the quiz.',
            isUser: false 
          }]);
        }
        break;

      default:
        message = `Processing ${file.name} for tutoring...`;
        try {
          setMessages(prev => [...prev, { text: message, isUser: true, isFileUpload: true }]);
          const result = await functionService.processTutoringDocument(file);
          setMessages(prev => [...prev, { 
            text: 'Document processed successfully! You can now ask questions about it.',
            isUser: false 
          }]);
        } catch (error) {
          setMessages(prev => [...prev, { 
            text: 'Sorry, I encountered an error processing your document.',
            isUser: false 
          }]);
        }
    }
    setIsLoading(false);
  };

  // Helper function to format quiz for display
  const formatQuiz = (quiz) => {
    return quiz.questions.map((q, i) => `
 **Question ${i + 1}:** ${q.question}
 
 ${q.options.map((opt, j) => `${['A', 'B', 'C', 'D'][j]}. ${opt}`).join('\n')}
 
 **Correct Answer:** ${['A', 'B', 'C', 'D'][q.correctAnswer]}
 
 **Explanation:** ${q.explanation}
 `).join('\n---\n');
  };

  /**
   * Xử lý khi người dùng gửi tin nhắn
   * - Thêm tin nhắn người dùng vào danh sách
   * - Gọi API gửi tin nhắn
   * - Xử lý phản hồi stream từ server
   * - Cập nhật UI với từng token nhận được
   */
  const handleSubmit = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);
    streamedMessageRef.current = '';

    setMessages(prev => [...prev, { text: userMessage, isUser: true }]);

    if (messages.length === 0) {
      onNewChat({
        id: threadId.current,
        title: userMessage.slice(0, 30) + (userMessage.length > 30 ? '...' : ''),
        timestamp: new Date(),
      });
    }

    try {
      setMessages(prev => [...prev, { text: '', isUser: false }]);

      // Xử lý khác nhau dựa trên function đang active
      switch (activeFunction) {
        case 'video':
          await handleVideoConversion(userMessage);
          break;
        case 'quiz':
          await handleQuizGeneration(userMessage);
          break;
        default:
          await handleTutorChat(userMessage);
      }

    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        text: 'Sorry, I encountered an error processing your request.',
        isUser: false 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTutorChat = async (message) => {
    await chatService.sendMessageStream(
      message,
      threadId.current,
      selectedModel,
      settings, // Pass all relevant settings
      (token) => {
        streamedMessageRef.current += token;
        setMessages(prev => {
          const newMessages = [...prev];
          const lastMessage = newMessages[newMessages.length - 1];
          lastMessage.text = streamedMessageRef.current;
          return newMessages;
        });
      },
      (error) => {
        console.error('Stream error:', error);
        setMessages(prev => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1].text = 'Sorry, I encountered an error processing your request.';
          return newMessages;
        });
      }
    );
  };

  const handleVideoConversion = async (message) => {
    if (!uploadedFile.current) {
      setMessages(prev => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1].text = 'Please upload your slides (PDF/PPTX) first before converting to video.';
        return newMessages;
      });
      return;
    }

    // Simulate video conversion by loading YouTube video
    setVideoId('wHkeTkSXBr8');
    setTranscript(`Introduction to Machine Learning...`);
    setShowVideoInterface(true);
    
    setMessages(prev => {
      const newMessages = [...prev];
      newMessages[newMessages.length - 1].text = 'Video has been loaded! You can now watch it and ask questions about the content.';
      return newMessages;
    });
  };

  const handleQuizGeneration = async (message) => {
    try {
      const result = await functionService.generateQuiz(message, settings);
      setQuizData(result);
      setShowQuizInterface(true);
      setMessages(prev => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1].text = 'Quiz has been generated! You can start now.';
        return newMessages;
      });
    } catch (error) {
      setMessages(prev => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1].text = 'Sorry, I encountered an error generating the quiz.';
        return newMessages;
      });
    }
  };

  const handleQuizComplete = (results) => {
    setMessages(prev => [...prev, {
      type: 'system',
      content: `Quiz completed! Your score: ${results.score}/${results.total}`,
      timestamp: new Date()
    }]);
    
    if (results.details) {
      setMessages(prev => [...prev, {
        type: 'system',
        content: `Detailed results: ${JSON.stringify(results.details)}`,
        timestamp: new Date()
      }]);
    }
  };

  /**
   * Effect tự động scroll đến tin nhắn cuối cùng
   * khi có tin nhắn mới
   */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Function descriptions for info text
  const getFunctionInfo = () => {
    switch (activeFunction) {
      case 'video':
        return 'Upload slides to convert them into a video lecture';
      case 'quiz':
        return 'Generate practice quizzes from your learning materials';
      default:
        return 'Ask questions about your course materials or upload documents for tutoring';
    }
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (isModelDropdownOpen && !event.target.closest('.model-selector')) {
        setIsModelDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isModelDropdownOpen]);

  const handleFunctionChange = (newFunction) => {
    onFunctionChange(newFunction); // Thông báo cho parent component
    // Reset message input và placeholder
    setInput('');
    // Reset streamed message
    streamedMessageRef.current = '';
    // Reset video state khi chuyển function
    setVideoId(null);
    setTranscript(null);
    setShowVideoInterface(false);
    setShowQuizInterface(false);
    uploadedFile.current = null;
  };

  // Cập nhật placeholder text dựa trên function đang active
  const getPlaceholderText = () => {
    switch (activeFunction) {
      case 'video':
        return "Upload slides or enter instructions for video conversion...";
      case 'quiz':
        return "Upload materials or enter topics for quiz generation...";
      default:
        return "Ask a question about your materials...";
    }
  };

  // Cập nhật accepted file types dựa trên function đang active
  const getAcceptedFileTypes = () => {
    switch (activeFunction) {
      case 'video':
        return ".pdf,.pptx";
      case 'quiz':
        return ".pdf,.doc,.docx,.txt,.pptx";
      default:
        return ".pdf,.doc,.docx,.txt,.pptx";
    }
  };

  // Expose resetChat method through ref
  React.useImperativeHandle(ref, () => ({
    resetChat: () => {
      setMessages([]);
      setInput('');
      setIsLoading(false);
      threadId.current = uuidv4();
      streamedMessageRef.current = '';
    }
  }));

  return (
    <ChatContainer>
      {activeFunction === 'video' && showVideoInterface && videoId ? (
        <VideoModeContainer>
          <VideoSection>
            <VideoPlayer
              videoId={videoId}
              transcript={transcript}
            />
          </VideoSection>
          <ChatSection>
            <Header>
              <HeaderTitle>AI Assistant</HeaderTitle>
            </Header>
            <MessagesContainer>
              {messages.map((message, index) => (
                <ChatMessage
                  key={index}
                  message={message}
                />
              ))}
              <div ref={messagesEndRef} />
            </MessagesContainer>
            <InputWrapper>
              <InputContainer>
                <FileInput
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileUpload}
                  accept=".pdf,.pptx"
                />
                <IconButton
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isLoading}
                >
                  <AttachFileIcon />
                </IconButton>
                <TextArea
                  value={input}
                  onChange={handleInputChange}
                  onKeyPress={handleKeyPress}
                  placeholder={uploadedFile.current 
                    ? "Provide instructions for video conversion..." 
                    : "Upload your slides first..."}
                  disabled={isLoading}
                />
                <IconButton
                  onClick={handleSubmit}
                  disabled={isLoading || !input.trim()}
                >
                  <SendIcon />
                </IconButton>
              </InputContainer>
            </InputWrapper>
          </ChatSection>
        </VideoModeContainer>
      ) : activeFunction === 'quiz' && showQuizInterface && quizData ? (
        <QuizInterface
          quiz={quizData}
          settings={settings}
          onComplete={handleQuizComplete}
        />
      ) : (
        <>
          <Header>
            <HeaderLeft>
              <HeaderTitle>
                {activeFunction === 'video' ? 'Slide to Video' : 
                 activeFunction === 'quiz' ? 'Quiz Generator' : 
                 'AI Tutor Chat'}
              </HeaderTitle>
            </HeaderLeft>
            <ModelSelector className="model-selector">
              <ModelButton onClick={() => setIsModelDropdownOpen(!isModelDropdownOpen)}>
                {models.find(m => m.id === selectedModel)?.name}
                <KeyboardArrowDownIcon style={{ 
                  transform: isModelDropdownOpen ? 'rotate(180deg)' : 'none',
                  transition: 'transform 0.3s ease'
                }} />
              </ModelButton>
              <ModelDropdown isOpen={isModelDropdownOpen}>
                {models.map(model => (
                  <ModelOption
                    key={model.id}
                    active={model.id === selectedModel}
                    onClick={() => handleModelSelect(model.id)}
                  >
                    {model.name}
                  </ModelOption>
                ))}
              </ModelDropdown>
            </ModelSelector>
          </Header>
          <MessagesContainer>
            {messages.length === 0 ? (
              <WelcomeMessage>
                <h1>Welcome to AI Tutor!</h1>
                <p>
                  I'm here to help you learn and understand your course materials.
                  You can upload documents or ask questions about your studies.
                </p>
              </WelcomeMessage>
            ) : (
              messages.map((message, index) => (
                <ChatMessage
                  key={index}
                  message={message}
                />
              ))
            )}
            <div ref={messagesEndRef} />
          </MessagesContainer>
          <FunctionBar>
            <FunctionContainer>
              <FunctionButton
                active={activeFunction === 'tutor'}
                onClick={() => handleFunctionChange('tutor')}
                disabled={hasStartedChat}
              >
                <SchoolIcon />
                AI Tutor
              </FunctionButton>
              <FunctionButton
                active={activeFunction === 'video'}
                onClick={() => handleFunctionChange('video')}
                disabled={hasStartedChat}
              >
                <VideoLibraryIcon />
                Slide to Video
              </FunctionButton>
              <FunctionButton
                active={activeFunction === 'quiz'}
                onClick={() => handleFunctionChange('quiz')}
                disabled={hasStartedChat}
              >
                <QuizIcon />
                Quiz Generator
              </FunctionButton>
            </FunctionContainer>
            <InfoText>
              <HelpIcon style={{ fontSize: 16, verticalAlign: 'middle', marginRight: 4 }} />
              {getFunctionInfo()}
            </InfoText>
          </FunctionBar>
          <InputWrapper>
            <InputContainer>
              <FileInput
                type="file"
                ref={fileInputRef}
                onChange={handleFileUpload}
                accept={getAcceptedFileTypes()}
              />
              <IconButton
                onClick={() => fileInputRef.current?.click()}
                disabled={isLoading}
              >
                <AttachFileIcon />
              </IconButton>
              <TextArea
                value={input}
                onChange={handleInputChange}
                onKeyPress={handleKeyPress}
                placeholder={getPlaceholderText()}
                disabled={isLoading}
              />
              <IconButton
                onClick={handleSubmit}
                disabled={isLoading || !input.trim()}
              >
                <SendIcon />
              </IconButton>
            </InputContainer>
          </InputWrapper>
        </>
      )}
    </ChatContainer>
  );
});

export default ChatBox; 