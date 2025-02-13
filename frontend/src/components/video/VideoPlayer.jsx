import React from 'react';
import styled from 'styled-components';

const VideoContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
`;

const MainContent = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
`;

const VideoWrapper = styled.div`
  position: relative;
  padding-top: 56.25%; /* 16:9 Aspect Ratio */
  background: #000;
  flex-shrink: 0;
`;

const StyledIframe = styled.iframe`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: none;
`;

const TranscriptContainer = styled.div`
  flex: 1;
  min-height: 0;
  background: white;
  border-top: 1px solid #e0e0e0;
  overflow-y: auto;
  padding: 16px 24px;
  
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

const TranscriptHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  position: sticky;
  top: 0;
  background: white;
  padding: 8px 0;
  z-index: 1;
`;

const TranscriptTitle = styled.h3`
  margin: 0;
  color: #1a237e;
  font-size: 1.1rem;
`;

const TranscriptText = styled.div`
  color: #333;
  font-size: 16px;
  line-height: 1.6;
  white-space: pre-wrap;
  padding-bottom: 16px;

  h1, h2, h3, h4, h5, h6 {
    color: #1a237e;
    margin: 24px 0 16px;
    &:first-child {
      margin-top: 0;
    }
  }

  ul, ol {
    padding-left: 24px;
    margin: 16px 0;
  }

  p {
    margin: 16px 0;
  }
`;

const VideoPlayer = ({ videoId, transcript }) => {
  return (
    <VideoContainer>
      <MainContent>
        <VideoWrapper>
          <StyledIframe
            src={`https://www.youtube.com/embed/${videoId}`}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </VideoWrapper>
        <TranscriptContainer>
          <TranscriptHeader>
            <TranscriptTitle>Video Transcript</TranscriptTitle>
          </TranscriptHeader>
          <TranscriptText>
            {transcript}
          </TranscriptText>
        </TranscriptContainer>
      </MainContent>
    </VideoContainer>
  );
};

export default VideoPlayer; 