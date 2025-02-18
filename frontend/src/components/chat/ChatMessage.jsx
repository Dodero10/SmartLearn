import React from 'react';
import styled from 'styled-components';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Avatar } from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import SmartToyIcon from '@mui/icons-material/SmartToy';

const FileUploadMessage = styled.div`
  padding: 8px 12px;
  background: #e3f2fd;
  border-radius: 6px;
  color: #1565c0;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const MessageContainer = styled.div`
  display: flex;
  gap: 16px;
  align-items: flex-start;
  max-width: 100%;
`;

const MessageContent = styled.div`
  flex: 1;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-wrap: break-word;
  background: ${props => props.isUser ? 'var(--primary-color)' : 'var(--message-background, #f0f0f0)'};
  color: ${props => props.isUser ? 'white' : 'var(--text-primary)'};
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 16px;
  line-height: 1.5;
  max-width: calc(100% - 80px);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);

  p {
    margin: 0 0 16px;
    white-space: pre-wrap;
    &:last-child {
      margin-bottom: 0;
    }
  }

  code {
    background-color: #f5f5f5;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Fira Code', monospace;
    font-size: 14px;
  }

  pre {
    margin: 16px 0;
    white-space: pre-wrap;
    
    code {
      background: transparent;
      padding: 0;
    }
  }

  ul, ol {
    margin: 8px 0;
    padding-left: 24px;
  }

  table {
    border-collapse: collapse;
    width: 100%;
    margin: 16px 0;

    th, td {
      border: 1px solid #e0e0e0;
      padding: 8px 12px;
      text-align: left;
    }

    th {
      background-color: #f5f5f5;
    }
  }
`;

const StyledAvatar = styled(Avatar)`
  width: 40px !important;
  height: 40px !important;
  background-color: ${props => props.isUser ? 'var(--primary-color)' : '#666'} !important;
`;

const CodeBlock = ({ language, value }) => {
  return (
    <SyntaxHighlighter
      language={language}
      style={atomDark}
      customStyle={{
        borderRadius: '8px',
        padding: '16px',
        margin: '16px 0',
      }}
    >
      {value}
    </SyntaxHighlighter>
  );
};

/**
 * Component hiển thị một tin nhắn trong cuộc trò chuyện
 * Hỗ trợ:
 * - Hiển thị tin nhắn người dùng và bot với style khác nhau
 * - Render markdown content
 * - Style cho code blocks, tables, lists
 * 
 * @param {Object} props - Props của component
 * @param {Object} props.message - Thông tin tin nhắn
 * @param {string} props.message.text - Nội dung tin nhắn
 * @param {boolean} props.isUser - Đánh dấu tin nhắn của người dùng hay bot
 */
const ChatMessage = React.memo(React.forwardRef(({ message, isUser }, ref) => {
  return (
    <MessageContainer>
      <StyledAvatar isUser={isUser}>
        {isUser ? <PersonIcon /> : <SmartToyIcon />}
      </StyledAvatar>
      <MessageContent isUser={isUser}>
        {message.isFileUpload ? (
          <FileUploadMessage>{message.text}</FileUploadMessage>
        ) : (
          <ReactMarkdown
            components={{
              p: ({ children }) => <p style={{ whiteSpace: 'pre-wrap' }}>{children}</p>,
              code: ({ node, inline, className, children, ...props }) => {
                const match = /language-(\w+)/.exec(className || '');
                return !inline && match ? (
                  <CodeBlock
                    language={match[1]}
                    value={String(children).replace(/\n$/, '')}
                    {...props}
                  />
                ) : (
                  <code className={className} {...props}>
                    {children}
                  </code>
                );
              }
            }}
          >
            {message.text}
          </ReactMarkdown>
        )}
      </MessageContent>
    </MessageContainer>
  );
}));

ChatMessage.displayName = 'ChatMessage';

export default ChatMessage;