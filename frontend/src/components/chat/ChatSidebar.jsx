import React, { useState } from 'react';
import styled from 'styled-components';
import DeleteIcon from '@mui/icons-material/Delete';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import CreateIcon from '@mui/icons-material/Create';
import SearchIcon from '@mui/icons-material/Search';
import CloseIcon from '@mui/icons-material/Close';
import NoteAddIcon from '@mui/icons-material/NoteAdd';

const SidebarContainer = styled.div`
  width: ${props => props.isOpen ? '280px' : '0'};
  height: 100%;
  background: var(--background-primary);
  border-right: 1px solid var(--border-color);
  transition: width 0.3s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
`;

const TopBar = styled.div`
  display: flex;
  gap: 8px;
  padding: 16px;
  align-items: center;
  justify-content: space-between;
`;

const TopBarTitle = styled.h2`
  margin: 0;
  color: var(--text-primary);
  font-size: 1.1rem;
  font-weight: 600;
  letter-spacing: -0.022em;
  flex: 1;
`;

const TopBarActions = styled.div`
  display: flex;
  gap: 8px;
  align-items: center;
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

const SearchButton = styled(NewChatButton)`
  background: rgba(0, 0, 0, 0.04);
  color: var(--text-secondary);
  box-shadow: none;

  &:hover {
    background: rgba(0, 0, 0, 0.08);
    transform: none;
    box-shadow: none;
  }

  &:active {
    background: rgba(0, 0, 0, 0.12);
    transform: none;
  }
`;

const ChatList = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 0 8px;

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
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: ${props => props.active ? '#f0f2ff' : 'transparent'};
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.active ? '#f0f2ff' : '#f5f5f5'};
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
  color: #1d1d1f;
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
  opacity: ${props => props.show ? 1 : 0};
  transition: all 0.2s ease;

  ${ChatItem}:hover & {
    opacity: 1;
  }

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
  opacity: 1;
  
  &:hover {
    background: #f0f2ff;
  }
`;

const FloatingContainer = styled.div`
  position: fixed;
  left: 12px;
  top: 24px;
  display: ${props => props.show ? 'flex' : 'none'};
  align-items: center;
  gap: 12px;
  z-index: 2;
`;

const FloatingTitle = styled.h2`
  margin: 0;
  color: var(--text-primary);
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: -0.022em;
`;

const FloatingNewChat = styled.button`
  background: white;
  border: none;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;

  &:hover {
    background: #f5f5f5;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  svg {
    font-size: 24px;
    color: var(--primary-color);
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
  const [searchTerm, setSearchTerm] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  
  const filteredChats = chatHistory.filter(chat => 
    chat.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const toggleSearch = () => {
    setIsSearching(!isSearching);
    if (!isSearching) {
      setSearchTerm('');
    }
  };

  return (
    <>
      <ToggleButton onClick={onToggle} isOpen={isOpen}>
        <ChevronLeftIcon />
      </ToggleButton>
      <SidebarContainer isOpen={isOpen}>
        <TopBar>
          <TopBarTitle>Chat History</TopBarTitle>
          <TopBarActions>
            <SearchButton onClick={toggleSearch}>
              <SearchIcon fontSize="small" />
            </SearchButton>
            <NewChatButton onClick={onNewChat}>
              <CreateIcon />
            </NewChatButton>
          </TopBarActions>
        </TopBar>
        <ChatList>
          {filteredChats.map((chat) => (
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
                show={chat.id === activeChatId}
              >
                <DeleteIcon style={{ fontSize: '18px' }} />
              </IconButton>
            </ChatItem>
          ))}
        </ChatList>
      </SidebarContainer>
    </>
  );
};

export default ChatSidebar; 