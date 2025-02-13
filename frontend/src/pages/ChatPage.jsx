import React, { useState, useRef } from 'react';
import ChatBox from '../components/chat/ChatBox';
import ChatSidebar from '../components/chat/ChatSidebar';
import RightSidebar from '../components/settings/RightSidebar';
import styled from 'styled-components';

const PageContainer = styled.div`
  height: 100%;
  background-color: #f8f9fa;
  display: flex;
`;

const MainContent = styled.div`
  flex: 1;
  display: flex;
  position: relative;
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

  const handleChatSelect = (chatId) => {
    setActiveChatId(chatId);
    // TODO: Load chat messages for the selected chat
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
      type: activeFunction
    };
    setChatHistory(prev => [...prev, newChat]);
  };

  const handleSettingsChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleStartNewChat = () => {
    setActiveChatId(null);
    setActiveFunction('tutor');
    if (chatBoxRef.current) {
      chatBoxRef.current.resetChat();
    }
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
        />
        <RightSidebar
          isOpen={isRightSidebarOpen}
          onToggle={() => setIsRightSidebarOpen(!isRightSidebarOpen)}
          activeFunction={activeFunction}
          settings={settings}
          onSettingsChange={handleSettingsChange}
        />
      </MainContent>
    </PageContainer>
  );
};

export default ChatPage;
