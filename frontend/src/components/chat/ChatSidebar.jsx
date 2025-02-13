import React from 'react';
import styled from 'styled-components';
import HistoryIcon from '@mui/icons-material/History';
import DeleteIcon from '@mui/icons-material/Delete';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import AddIcon from '@mui/icons-material/Add';

const SidebarContainer = styled.div`
  width: ${props => props.isOpen ? '280px' : '0'};
  height: 100%;
  background: white;
  border-right: 1px solid #e0e0e0;
  transition: width 0.3s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

const HeaderContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
`;

const HeaderTitle = styled.h3`
  margin: 0;
  color: #1a237e;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ChatList = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 16px;

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

const ChatTypeIndicator = styled.span`
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
  background: ${props => {
    switch (props.type) {
      case 'tutor': return '#e3f2fd';
      case 'video': return '#e8f5e9';
      case 'quiz': return '#fff3e0';
      default: return '#f5f5f5';
    }
  }};
  color: ${props => {
    switch (props.type) {
      case 'tutor': return '#1565c0';
      case 'video': return '#2e7d32';
      case 'quiz': return '#ef6c00';
      default: return '#616161';
    }
  }};
  margin-left: 8px;
`;

const ChatItem = styled.div`
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: ${props => props.active ? '#f0f2ff' : 'transparent'};

  &:hover {
    background: #f0f2ff;
  }
`;

const ChatItemLeft = styled.div`
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
`;

const ChatTitle = styled.div`
  font-size: 14px;
  color: #333;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const IconButton = styled.button`
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  color: #666;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background: rgba(0, 0, 0, 0.05);
    color: ${props => props.delete ? '#d32f2f' : '#1a237e'};
  }
`;

const ToggleButton = styled(IconButton)`
  position: absolute;
  left: ${props => props.isOpen ? '280px' : '0'};
  top: 50%;
  transform: translateY(-50%) ${props => props.isOpen ? 'none' : 'rotate(180deg)'};
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: left 0.3s ease, transform 0.3s ease;
  z-index: 1;
  width: 24px;
  height: 48px;
  border-radius: ${props => props.isOpen ? '0 8px 8px 0' : '8px 0 0 8px'};
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: #f0f2ff;
  }
`;

const NewChatButton = styled.button`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid #1a237e;
  border-radius: 6px;
  background: #f0f2ff;
  color: #1a237e;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: #1a237e;
    color: white;
  }

  svg {
    font-size: 18px;
  }
`;

const ChatSidebar = ({ 
  isOpen, 
  onToggle, 
  chatHistory, 
  activeChatId,
  onChatSelect,
  onChatDelete,
  onNewChat
}) => {
  return (
    <>
      <ToggleButton onClick={onToggle} isOpen={isOpen}>
        <ChevronLeftIcon />
      </ToggleButton>
      <SidebarContainer isOpen={isOpen}>
        <HeaderContainer>
          <HeaderTitle>
            <HistoryIcon fontSize="small" />
            Chat History
          </HeaderTitle>
          <NewChatButton onClick={onNewChat}>
            <AddIcon />
            New Chat
          </NewChatButton>
        </HeaderContainer>
        <ChatList>
          {chatHistory.map((chat) => (
            <ChatItem 
              key={chat.id}
              active={chat.id === activeChatId}
              onClick={() => onChatSelect(chat.id)}
            >
              <ChatItemLeft>
                <ChatTitle>{chat.title || 'New Chat'}</ChatTitle>
                <ChatTypeIndicator type={chat.type}>
                  {chat.type === 'tutor' ? 'AI Tutor' :
                   chat.type === 'video' ? 'Video' :
                   chat.type === 'quiz' ? 'Quiz' : ''}
                </ChatTypeIndicator>
              </ChatItemLeft>
              <IconButton 
                delete 
                onClick={(e) => {
                  e.stopPropagation();
                  onChatDelete(chat.id);
                }}
              >
                <DeleteIcon fontSize="small" />
              </IconButton>
            </ChatItem>
          ))}
        </ChatList>
      </SidebarContainer>
    </>
  );
};

export default ChatSidebar; 