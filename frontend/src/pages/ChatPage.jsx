import React, { useState, useRef } from 'react';
import ChatBox from '../components/chat/ChatBox';
import ChatSidebar from '../components/chat/ChatSidebar';
import RightSidebar from '../components/settings/RightSidebar';
import styled from 'styled-components';

const PageContainer = styled.div`
  height: 100%;
  background-color: transparent;
  display: flex;
  gap: 16px;
  padding: 16px;
  
  @media (max-width: 768px) {
    padding: 8px;
    gap: 8px;
  }
`;

const MainContent = styled.div`
  flex: 1;
  display: flex;
  position: relative;
  background: var(--blur-background);
  backdrop-filter: blur(25px) saturate(180%);
  -webkit-backdrop-filter: blur(25px) saturate(180%);
  border-radius: 20px;
  box-shadow: 
    0 2px 5px rgba(0, 0, 0, 0.02),
    0 8px 24px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(255, 255, 255, 0.5);
  
  @media (max-width: 768px) {
    border-radius: 16px;
  }

  &:hover {
    box-shadow: 
      0 2px 5px rgba(0, 0, 0, 0.04),
      0 12px 32px rgba(0, 0, 0, 0.12);
  }
`;

/**
 * Trang chính của ứng dụng chat
 * Bao gồm:
 * - Layout trang
 * - Component ChatBox để xử lý chat
 */
const ChatPage = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isRightSidebarOpen, setIsRightSidebarOpen] = useState(true);
  const [chatHistory, setChatHistory] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [activeFunction, setActiveFunction] = useState('tutor');
  const [settings, setSettings] = useState({
    openaiKey: '',
    anthropicKey: '',
    temperature: 0.7,
    responseStyle: 'balanced',
    voice: 'female1',
    speakingRate: 1,
    slideTime: 30,
    videoQuality: 'high',
    voiceLanguage: 'en-US',
    voicePitch: 0,
    backgroundMusic: 'none',
    musicVolume: 30,
    questionCount: 10,
    timePerQuestion: 60,
    difficulty: 'medium',
    topicFocus: 'all',
    questionType: 'mixed',
    includeExplanations: 'correct',
    quizFormat: 'standard'
  });

  const chatBoxRef = useRef(null);

  // Thêm state để lưu trữ danh sách files từ server
  const [serverFiles, setServerFiles] = useState([]);

  const handleChatSelect = (chatId) => {
    setActiveChatId(chatId);
  };

  const handleChatDelete = (chatId) => {
    setChatHistory(prev => prev.filter(chat => chat.id !== chatId));
    if (activeChatId === chatId) {
      setActiveChatId(null);
    }
  };

  const handleNewChat = (chatData) => {
    const newChat = {
      ...chatData,
      type: activeFunction,
      uploadedFiles: [], // Initialize empty files array for new chat
      messages: [] // Initialize empty messages array
    };
    setChatHistory(prev => [...prev, newChat]);
    setActiveChatId(chatData.id);
  };

  const handleSettingsChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleStartNewChat = () => {
    setActiveChatId(null);
    const newChatId = Date.now().toString();
    const newChat = {
      id: newChatId,
      title: 'New Chat',
      timestamp: new Date(),
      type: activeFunction,
      messages: []
    };
    setChatHistory(prev => [...prev, newChat]);
    setActiveChatId(newChatId);
    if (chatBoxRef.current) {
      chatBoxRef.current.resetChat();
    }
  };

  const handleUploadFiles = async (files) => {
    const newFiles = Array.from(files).map(file => ({
      file,
      name: file.name,
      type: file.type,
      selected: true,
      lastModified: file.lastModified
    }));

    if (!activeChatId) {
      // Tạo chat mới với files đã upload
      const newChatId = Date.now().toString();
      const newChat = {
        id: newChatId,
        title: activeFunction === 'quiz' ? 'New Quiz' : 'New Chat',
        timestamp: new Date(),
        type: activeFunction,
        uploadedFiles: newFiles,
        messages: [],
        quizState: activeFunction === 'quiz' ? {
          status: 'preparing',
          questions: [],
          currentQuestion: 0,
          score: 0,
          answers: []
        } : null
      };
      setChatHistory(prev => [...prev, newChat]);
      setActiveChatId(newChatId);

      // Nếu là quiz, tự động gửi tin nhắn yêu cầu tạo quiz
      if (activeFunction === 'quiz') {
        const fileNames = newFiles.map(f => f.name).join(', ');
        const message = {
          id: Date.now().toString(),
          text: `Please generate a quiz from these files: ${fileNames}`,
          isUser: true,
          timestamp: new Date()
        };
        setChatHistory(prev => 
          prev.map(chat => 
            chat.id === newChatId 
              ? { ...chat, messages: [...chat.messages, message] }
              : chat
          )
        );
      }
      return;
    }
    
    // Thêm files vào chat hiện tại
    setChatHistory(prev => {
      return prev.map(chat => {
        if (chat.id === activeChatId) {
          const existingFiles = Array.isArray(chat.uploadedFiles) ? chat.uploadedFiles : [];
          return {
            ...chat,
            uploadedFiles: [...existingFiles, ...newFiles]
          };
        }
        return chat;
      });
    });
  };

  const handleRemoveFile = (fileName) => {
    if (!activeChatId) return;

    setChatHistory(prev => prev.map(chat => {
      if (chat.id === activeChatId && Array.isArray(chat.uploadedFiles)) {
        const updatedChat = {
          ...chat,
          uploadedFiles: chat.uploadedFiles.filter(file => file.name !== fileName)
        };

        // Nếu là quiz và đang trong trạng thái preparing, cập nhật tin nhắn
        if (chat.type === 'quiz' && chat.quizState?.status === 'preparing') {
          const message = {
            id: Date.now().toString(),
            text: `Please remove ${fileName} from quiz generation`,
            isUser: true,
            timestamp: new Date()
          };
          updatedChat.messages = [...updatedChat.messages, message];
        }

        return updatedChat;
      }
      return chat;
    }));
  };

  const handleToggleFileSelection = (fileName) => {
    if (!activeChatId) return;

    setChatHistory(prev => prev.map(chat => {
      if (chat.id === activeChatId && Array.isArray(chat.uploadedFiles)) {
        return {
          ...chat,
          uploadedFiles: chat.uploadedFiles.map(file => 
            file.name === fileName ? { ...file, selected: !file.selected } : file
          )
        };
      }
      return chat;
    }));
  };

  // Get current chat's files with safety checks
  const currentChat = chatHistory.find(chat => chat.id === activeChatId);
  const currentFiles = Array.isArray(currentChat?.uploadedFiles) ? currentChat.uploadedFiles : [];

  // Thêm hàm để cập nhật danh sách files
  const handleServerFiles = (files) => {
    setServerFiles(files);
  };

  return (
    <PageContainer>
      <ChatSidebar
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
        chatHistory={chatHistory}
        activeChatId={activeChatId}
        onChatSelect={handleChatSelect}
        onChatDelete={handleChatDelete}
        onNewChat={handleStartNewChat}
      />
      <MainContent>
        <ChatBox
          ref={chatBoxRef}
          onNewChat={handleNewChat}
          activeChatId={activeChatId}
          activeFunction={activeFunction}
          onFunctionChange={setActiveFunction}
          settings={settings}
          uploadedFiles={currentFiles}
          onUploadFiles={handleUploadFiles}
          onRemoveFile={handleRemoveFile}
          chatHistory={chatHistory}
          isSidebarOpen={isSidebarOpen}
          onStartNewChat={handleStartNewChat}
        />
        <RightSidebar
          isOpen={isRightSidebarOpen}
          onToggle={() => setIsRightSidebarOpen(!isRightSidebarOpen)}
          activeFunction={activeFunction}
          settings={settings}
          onSettingsChange={handleSettingsChange}
          uploadedFiles={currentFiles}
          onRemoveFile={handleRemoveFile}
          onUploadFiles={handleUploadFiles}
          activeChatId={activeChatId}
          serverFiles={serverFiles}
          onServerFilesUpdate={handleServerFiles}
        />
      </MainContent>
    </PageContainer>
  );
};

export default ChatPage;
