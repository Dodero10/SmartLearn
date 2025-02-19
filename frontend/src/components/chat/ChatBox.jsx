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
import NoteAddIcon from '@mui/icons-material/NoteAdd';
import CreateIcon from '@mui/icons-material/Create';

const ChatContainer = styled.div`
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: transparent;
`;

const Header = styled.div`
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--blur-background);
  backdrop-filter: blur(25px) saturate(180%);
  -webkit-backdrop-filter: blur(25px) saturate(180%);
  position: sticky;
  top: 0;
  z-index: 10;
`;

const HeaderLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const HeaderTitle = styled.h2`
  margin: 0;
  color: var(--text-primary);
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: -0.022em;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const NewChatButton = styled.button`
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 10px;
  background: var(--primary-color);
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 102, 204, 0.15);

  &:hover {
    background: #0055b3;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 102, 204, 0.2);
  }

  &:active {
    transform: translateY(0);
    box-shadow: 0 1px 2px rgba(0, 102, 204, 0.15);
  }

  svg {
    font-size: 20px;
  }
`;

const ModelSelector = styled.div`
  position: relative;
`;

const ModelButton = styled.button`
  background: rgba(0, 0, 0, 0.04);
  border: none;
  padding: 8px 16px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(0, 0, 0, 0.06);
  }

  &:active {
    background: rgba(0, 0, 0, 0.08);
  }
`;

const ModelDropdown = styled.div`
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: var(--blur-background);
  backdrop-filter: blur(25px) saturate(180%);
  -webkit-backdrop-filter: blur(25px) saturate(180%);
  border-radius: 16px;
  box-shadow: 
    0 4px 8px rgba(0, 0, 0, 0.04),
    0 12px 32px rgba(0, 0, 0, 0.12);
  z-index: 10;
  min-width: 220px;
  display: ${props => props.isOpen ? 'block' : 'none'};
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.5);
`;

const ModelOption = styled.div`
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: ${props => props.active ? 'var(--primary-color)' : 'var(--text-primary)'};
  background: ${props => props.active ? 'rgba(0, 102, 204, 0.08)' : 'transparent'};
  font-weight: ${props => props.active ? '500' : 'normal'};

  &:hover {
    background: rgba(0, 0, 0, 0.04);
  }

  &:active {
    background: rgba(0, 0, 0, 0.06);
  }
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background-color: transparent;
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;

  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.15);
    border-radius: 4px;
    border: 2px solid transparent;
    background-clip: padding-box;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 0, 0, 0.25);
    border: 2px solid transparent;
    background-clip: padding-box;
  }
`;

const MessageContent = styled.div`
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-wrap: break-word;
  max-width: 100%;
  line-height: 1.5;
  font-size: 16px;
  padding: 12px 16px;
  background: var(--message-background);
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
`;

const InputWrapper = styled.div`
  border-top: 1px solid var(--border-color);
  padding: 16px 24px 24px;
  background: var(--blur-background);
  backdrop-filter: blur(25px) saturate(180%);
  -webkit-backdrop-filter: blur(25px) saturate(180%);
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
  padding: 14px 16px;
  border: 1px solid var(--border-color);
  border-radius: 16px;
  font-size: 16px;
  line-height: 1.47059;
  resize: none;
  height: 56px;
  max-height: 200px;
  overflow-y: auto;
  transition: all 0.2s ease;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: var(--text-primary);

  &:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 4px rgba(0, 102, 204, 0.15);
  }

  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.15);
    border-radius: 4px;
    border: 2px solid transparent;
    background-clip: padding-box;
  }
`;

const IconButton = styled.button`
  background: none;
  border: none;
  padding: 12px;
  cursor: pointer;
  color: ${props => props.disabled ? 'var(--text-secondary)' : 'var(--primary-color)'};
  transition: all 0.2s ease;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;

  &:hover:not(:disabled) {
    background: rgba(0, 102, 204, 0.08);
  }

  &:active:not(:disabled) {
    background: rgba(0, 102, 204, 0.12);
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
  color: var(--text-secondary);
  font-size: 15px;
  line-height: 1.47059;
  letter-spacing: -0.022em;
  max-width: 600px;
  margin: 0 auto;
  padding: 48px 24px;
`;

const FunctionBar = styled.div`
  padding: 12px 24px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid rgba(0, 0, 0, 0.1);
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
  border: none;
  border-radius: 10px;
  background: ${props => props.active ? 'rgba(0, 122, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)'};
  color: ${props => props.active ? '#007AFF' : '#666'};
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  font-weight: 500;

  &:hover {
    background: ${props => props.active ? 'rgba(0, 122, 255, 0.15)' : 'rgba(0, 0, 0, 0.08)'};
  }

  &:active {
    background: ${props => props.active ? 'rgba(0, 122, 255, 0.2)' : 'rgba(0, 0, 0, 0.12)'};
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

const CHAT_FUNCTIONS = {
  CHAT: 'chat',
  AI_TUTOR: 'ai_tutor',
  VIDEO: 'video',
  QUIZ: 'quiz'
};

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
  chatHistory,
  uploadedFiles,
  onUploadFiles,
  onRemoveFile,
  isSidebarOpen,
  onStartNewChat
}, ref) => {
  // State lưu trữ danh sách tin nhắn
  const [messages, setMessages] = useState([]);
  // State lưu trữ nội dung đang nhập
  const [inputValue, setInputValue] = useState('');
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
  const [selectedFunction, setSelectedFunction] = useState(CHAT_FUNCTIONS.CHAT);
  const modelDropdownRef = useRef(null);
  const [showVideo, setShowVideo] = useState(false);
  const [videoUrl, setVideoUrl] = useState('');
  const [showQuiz, setShowQuiz] = useState(false);
  
  // Kiểm tra xem cuộc hội thoại đã bắt đầu chưa
  const hasStartedChat = messages.length > 0;

  const models = [
    { id: 'gpt-4', name: 'GPT-4' },
    { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo' },
    { id: 'claude-3', name: 'Claude 3' },
    { id: 'deepseek', name: 'DeepSeek' },
    { id: 'Gemini-1.5-Flash', name: 'Gemini 1.5 Flash' },
  ];

  const handleModelSelect = (modelId) => {
    setSelectedModel(modelId);
    setIsModelDropdownOpen(false);
  };

  // Reset messages when activeChatId changes
  useEffect(() => {
    if (activeChatId) {
      const currentChat = chatHistory.find(chat => chat.id === activeChatId);
      setMessages(currentChat?.messages || []);
    } else {
      setMessages([]);
    }
  }, [activeChatId, chatHistory]);

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
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
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    try {
      setIsLoading(true);
      
      // Upload từng file
      for (const file of files) {
        await chatService.uploadFile(file);
      }
      
      // Thông báo lên component cha
      onUploadFiles?.(files);
    } catch (error) {
      console.error('Error uploading files:', error);
    } finally {
      setIsLoading(false);
    }
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
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: uuidv4(),
      text: inputValue,
      isUser: true
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    const botMessage = {
      id: uuidv4(),
      text: '',
      isUser: false
    };

    setMessages(prev => [...prev, botMessage]);

    try {
      switch (selectedFunction) {
        case CHAT_FUNCTIONS.CHAT:
          await handleNormalChat(userMessage.text, botMessage.id);
          break;
        case CHAT_FUNCTIONS.AI_TUTOR:
          await handleTutorChat(userMessage.text, botMessage.id);
          break;
        case CHAT_FUNCTIONS.VIDEO:
          await handleVideoConversion(userMessage.text);
          break;
        case CHAT_FUNCTIONS.QUIZ:
          await handleQuizGeneration(userMessage.text);
          break;
        default:
          await handleNormalChat(userMessage.text, botMessage.id);
      }
    } catch (error) {
      console.error('Error in chat:', error);
      setMessages(prev => 
        prev.map(msg => 
          msg.id === botMessage.id 
            ? { ...msg, text: 'Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại.' }
            : msg
        )
      );
    }

    setIsLoading(false);
  };

  const handleTutorChat = async (message, botMessageId) => {
    try {
      await chatService.sendAITutorQuery(
        message,
        (token) => {
          setMessages(prev =>
            prev.map(msg =>
              msg.id === botMessageId
                ? { ...msg, text: msg.text + token }
                : msg
            )
          );
        },
        (error) => {
          setMessages(prev =>
            prev.map(msg =>
              msg.id === botMessageId
                ? { ...msg, text: 'Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại.' }
                : msg
            )
          );
        }
      );
    } catch (error) {
      console.error('Error in AI Tutor chat:', error);
      throw error;
    }
  };

  const handleVideoConversion = async (message) => {
    if (uploadedFiles.length === 0) {
      setMessages(prev => {
        const newMessages = [...prev];
        if (newMessages.length > 0) {
          newMessages[newMessages.length - 1].text = 'Please upload your slides (PDF/PPTX) first before converting to video.';
        }
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
      if (newMessages.length > 0) {
        newMessages[newMessages.length - 1].text = 'Video has been loaded! You can now watch it and ask questions about the content.';
      }
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
        if (newMessages.length > 0) {
          newMessages[newMessages.length - 1].text = 'Quiz has been generated! You can start now.';
        }
        return newMessages;
      });
    } catch (error) {
      setMessages(prev => {
        const newMessages = [...prev];
        if (newMessages.length > 0) {
          newMessages[newMessages.length - 1].text = 'Sorry, I encountered an error generating the quiz.';
        }
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
    switch (selectedFunction) {
      case CHAT_FUNCTIONS.CHAT:
        return {
          icon: <SchoolIcon />,
          title: 'Chat thông thường',
          placeholder: 'Nhập tin nhắn...'
        };
      case CHAT_FUNCTIONS.AI_TUTOR:
        return {
          icon: <HelpIcon />,
          title: 'AI Tutor',
          placeholder: 'Hỏi AI Tutor của bạn...'
        };
      case CHAT_FUNCTIONS.VIDEO:
        return {
          icon: <VideoLibraryIcon />,
          title: 'Tạo video',
          placeholder: 'Tải lên slide để tạo video...'
        };
      case CHAT_FUNCTIONS.QUIZ:
        return {
          icon: <QuizIcon />,
          title: 'Tạo quiz',
          placeholder: 'Tải lên tài liệu để tạo quiz...'
        };
      default:
        return {
          icon: <SchoolIcon />,
          title: 'Chat thông thường',
          placeholder: 'Nhập tin nhắn...'
        };
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
    onFunctionChange(newFunction);
    setInputValue('');
    streamedMessageRef.current = '';
    setVideoId(null);
    setTranscript(null);
    setShowVideoInterface(false);
    setShowQuizInterface(false);
    setSelectedFunction(newFunction);
  };

  // Cập nhật placeholder text dựa trên function đang active
  const getPlaceholderText = () => {
    switch (selectedFunction) {
      case CHAT_FUNCTIONS.CHAT:
        return "Nhập tin nhắn...";
      case CHAT_FUNCTIONS.AI_TUTOR:
        return "Hỏi AI Tutor của bạn...";
      case CHAT_FUNCTIONS.VIDEO:
        return "Tải lên slide để tạo video...";
      case CHAT_FUNCTIONS.QUIZ:
        return "Tải lên tài liệu để tạo quiz...";
      default:
        return "Nhập tin nhắn...";
    }
  };

  // Cập nhật accepted file types dựa trên function đang active
  const getAcceptedFileTypes = () => {
    switch (selectedFunction) {
      case CHAT_FUNCTIONS.VIDEO:
        return ".pdf,.pptx";
      case CHAT_FUNCTIONS.QUIZ:
        return ".pdf,.doc,.docx,.txt,.pptx";
      default:
        return ".pdf,.doc,.docx,.txt,.pptx";
    }
  };

  // Expose resetChat method through ref
  React.useImperativeHandle(ref, () => ({
    resetChat: () => {
      setMessages([]);
      setInputValue('');
      setIsLoading(false);
      threadId.current = uuidv4();
      streamedMessageRef.current = '';
    }
  }));

  const handleNormalChat = async (message, botMessageId) => {
    try {
      await chatService.sendMessageStream(
        message,
        threadId.current,
        selectedModel,
        (token) => {
          setMessages(prev =>
            prev.map(msg =>
              msg.id === botMessageId
                ? { ...msg, text: msg.text + token }
                : msg
            )
          );
        },
        (error) => {
          setMessages(prev =>
            prev.map(msg =>
              msg.id === botMessageId
                ? { ...msg, text: 'Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại.' }
                : msg
            )
          );
        }
      );
    } catch (error) {
      console.error('Error in normal chat:', error);
      throw error;
    }
  };

  return (
    <ChatContainer>
      {selectedFunction === CHAT_FUNCTIONS.VIDEO && showVideoInterface && videoId ? (
        <VideoModeContainer>
          <VideoSection>
            <VideoPlayer
              videoId={videoId}
              transcript={transcript}
            />
          </VideoSection>
          <ChatSection>
            <Header>
              <HeaderLeft>
                {!isSidebarOpen && (
                  <NewChatButton onClick={onStartNewChat}>
                    <CreateIcon />
                  </NewChatButton>
                )}
                <HeaderTitle>
                  {selectedFunction === CHAT_FUNCTIONS.VIDEO ? 'Slide to Video' : 
                   selectedFunction === CHAT_FUNCTIONS.QUIZ ? 'Quiz Generator' : 
                   'AI Tutor Chat'}
                </HeaderTitle>
              </HeaderLeft>
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
                <TextArea
                  value={inputValue}
                  onChange={handleInputChange}
                  onKeyPress={handleKeyPress}
                  placeholder={uploadedFiles.length > 0 ? "Provide instructions for video conversion..." : "Upload your slides first..."}
                  disabled={isLoading}
                />
                <IconButton
                  onClick={handleSubmit}
                  disabled={isLoading || !inputValue.trim()}
                >
                  <SendIcon />
                </IconButton>
              </InputContainer>
            </InputWrapper>
          </ChatSection>
        </VideoModeContainer>
      ) : selectedFunction === CHAT_FUNCTIONS.QUIZ && showQuizInterface && quizData ? (
        <QuizInterface
          quiz={quizData}
          settings={settings}
          onComplete={handleQuizComplete}
        />
      ) : (
        <>
          <Header>
            <HeaderLeft>
              {!isSidebarOpen && (
                <NewChatButton onClick={onStartNewChat}>
                  <CreateIcon />
                </NewChatButton>
              )}
              <HeaderTitle>
                {selectedFunction === CHAT_FUNCTIONS.VIDEO ? 'Slide to Video' : 
                 selectedFunction === CHAT_FUNCTIONS.QUIZ ? 'Quiz Generator' : 
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
              <ModelDropdown isOpen={isModelDropdownOpen} ref={modelDropdownRef}>
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
                active={selectedFunction === CHAT_FUNCTIONS.AI_TUTOR}
                onClick={() => handleFunctionChange(CHAT_FUNCTIONS.AI_TUTOR)}
                disabled={hasStartedChat}
              >
                <SchoolIcon />
                AI Tutor
              </FunctionButton>
              <FunctionButton
                active={selectedFunction === CHAT_FUNCTIONS.VIDEO}
                onClick={() => handleFunctionChange(CHAT_FUNCTIONS.VIDEO)}
                disabled={hasStartedChat}
              >
                <VideoLibraryIcon />
                Slide to Video
              </FunctionButton>
              <FunctionButton
                active={selectedFunction === CHAT_FUNCTIONS.QUIZ}
                onClick={() => handleFunctionChange(CHAT_FUNCTIONS.QUIZ)}
                disabled={hasStartedChat}
              >
                <QuizIcon />
                Quiz Generator
              </FunctionButton>
            </FunctionContainer>
            <InfoText>
              <HelpIcon style={{ fontSize: 16, verticalAlign: 'middle', marginRight: 4 }} />
              {getFunctionInfo().title}
            </InfoText>
          </FunctionBar>
          <InputWrapper>
            <InputContainer>
              <TextArea
                value={inputValue}
                onChange={handleInputChange}
                onKeyPress={handleKeyPress}
                placeholder={getPlaceholderText()}
                disabled={isLoading}
              />
              <IconButton
                onClick={handleSubmit}
                disabled={isLoading || !inputValue.trim()}
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