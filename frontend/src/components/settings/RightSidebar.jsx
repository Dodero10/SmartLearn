import React, { useState } from 'react';
import styled from 'styled-components';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import SettingsIcon from '@mui/icons-material/Settings';
import KeyIcon from '@mui/icons-material/Key';
import TimerIcon from '@mui/icons-material/Timer';
import QuizIcon from '@mui/icons-material/Quiz';

const SidebarContainer = styled.div`
  width: ${props => props.isOpen ? '300px' : '0'};
  height: 100%;
  background: white;
  border-left: 1px solid #e0e0e0;
  transition: width 0.3s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

const SidebarHeader = styled.div`
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const HeaderTitle = styled.h3`
  margin: 0;
  color: #1a237e;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const SettingsContainer = styled.div`
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

const Section = styled.div`
  margin-bottom: 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
`;

const SectionHeader = styled.div`
  padding: 12px 16px;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  user-select: none;

  &:hover {
    background: #f0f2ff;
  }

  svg {
    transform: ${props => props.isOpen ? 'rotate(-90deg)' : 'rotate(90deg)'};
    transition: transform 0.3s ease;
  }
`;

const SectionTitle = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1a237e;
  font-weight: 500;
`;

const SectionContent = styled.div`
  padding: ${props => props.isOpen ? '16px' : '0'};
  max-height: ${props => props.isOpen ? '500px' : '0'};
  transition: all 0.3s ease;
  overflow: hidden;
`;

const InputGroup = styled.div`
  margin-bottom: 16px;

  &:last-child {
    margin-bottom: 0;
  }
`;

const Label = styled.label`
  display: block;
  margin-bottom: 8px;
  color: #666;
  font-size: 14px;
`;

const Input = styled.input`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;

  &:focus {
    outline: none;
    border-color: #1a237e;
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  background: white;

  &:focus {
    outline: none;
    border-color: #1a237e;
  }
`;

const Slider = styled.input.attrs({ type: 'range' })`
  width: 100%;
  margin: 8px 0;
`;

const ToggleButton = styled.button`
  position: absolute;
  right: ${props => props.isOpen ? '300px' : '0'};
  top: 50%;
  transform: translateY(-50%);
  background: white;
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 24px;
  height: 48px;
  border-radius: ${props => props.isOpen ? '8px 0 0 8px' : '0 8px 8px 0'};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
  transition: right 0.3s ease;

  &:hover {
    background: #f0f2ff;
  }

  svg {
    transform: ${props => props.isOpen ? 'rotate(180deg)' : 'rotate(0deg)'};
    transition: transform 0.3s ease;
  }
`;

const RightSidebar = ({ isOpen, onToggle, activeFunction, settings, onSettingsChange }) => {
  const [expandedSections, setExpandedSections] = useState(['apiKeys']);

  const toggleSection = (section) => {
    setExpandedSections(prev => 
      prev.includes(section) 
        ? prev.filter(s => s !== section)
        : [...prev, section]
    );
  };

  const isSectionExpanded = (section) => expandedSections.includes(section);

  return (
    <>
      <ToggleButton onClick={onToggle} isOpen={isOpen}>
        <ChevronRightIcon />
      </ToggleButton>
      <SidebarContainer isOpen={isOpen}>
        <SidebarHeader>
          <HeaderTitle>
            <SettingsIcon fontSize="small" />
            Settings
          </HeaderTitle>
        </SidebarHeader>
        <SettingsContainer>
          {/* API Keys Section */}
          <Section>
            <SectionHeader onClick={() => toggleSection('apiKeys')}>
              <SectionTitle>
                <KeyIcon fontSize="small" />
                API Keys
              </SectionTitle>
              <ChevronRightIcon 
                style={{ 
                  transform: isSectionExpanded('apiKeys') ? 'rotate(-90deg)' : 'rotate(90deg)',
                  transition: 'transform 0.3s ease'
                }} 
              />
            </SectionHeader>
            <SectionContent isOpen={isSectionExpanded('apiKeys')}>
              <InputGroup>
                <Label>OpenAI API Key</Label>
                <Input 
                  type="password"
                  value={settings.openaiKey || ''}
                  onChange={e => onSettingsChange('openaiKey', e.target.value)}
                  placeholder="sk-..."
                />
              </InputGroup>
              <InputGroup>
                <Label>Anthropic API Key</Label>
                <Input 
                  type="password"
                  value={settings.anthropicKey || ''}
                  onChange={e => onSettingsChange('anthropicKey', e.target.value)}
                  placeholder="sk-ant-..."
                />
              </InputGroup>
            </SectionContent>
          </Section>

          {/* AI Tutor Settings */}
          {activeFunction === 'tutor' && (
            <Section>
              <SectionHeader onClick={() => toggleSection('tutorSettings')}>
                <SectionTitle>
                  <SettingsIcon fontSize="small" />
                  AI Tutor Settings
                </SectionTitle>
                <ChevronRightIcon 
                  style={{ 
                    transform: isSectionExpanded('tutorSettings') ? 'rotate(-90deg)' : 'rotate(90deg)',
                    transition: 'transform 0.3s ease'
                  }} 
                />
              </SectionHeader>
              <SectionContent isOpen={isSectionExpanded('tutorSettings')}>
                <InputGroup>
                  <Label>Temperature ({settings.temperature || 0.7})</Label>
                  <Slider
                    min="0"
                    max="2"
                    step="0.1"
                    value={settings.temperature || 0.7}
                    onChange={e => onSettingsChange('temperature', e.target.value)}
                  />
                </InputGroup>
                <InputGroup>
                  <Label>Response Style</Label>
                  <Select
                    value={settings.responseStyle || 'balanced'}
                    onChange={e => onSettingsChange('responseStyle', e.target.value)}
                  >
                    <option value="concise">Concise</option>
                    <option value="balanced">Balanced</option>
                    <option value="detailed">Detailed</option>
                  </Select>
                </InputGroup>
              </SectionContent>
            </Section>
          )}

          {/* Video Conversion Settings */}
          {activeFunction === 'video' && (
            <Section>
              <SectionHeader onClick={() => toggleSection('videoSettings')}>
                <SectionTitle>
                  <TimerIcon fontSize="small" />
                  Video Settings
                </SectionTitle>
                <ChevronRightIcon 
                  style={{ 
                    transform: isSectionExpanded('videoSettings') ? 'rotate(-90deg)' : 'rotate(90deg)',
                    transition: 'transform 0.3s ease'
                  }} 
                />
              </SectionHeader>
              <SectionContent isOpen={isSectionExpanded('videoSettings')}>
                <InputGroup>
                  <Label>Video Quality</Label>
                  <Select
                    value={settings.videoQuality || 'high'}
                    onChange={e => onSettingsChange('videoQuality', e.target.value)}
                  >
                    <option value="low">Low (480p)</option>
                    <option value="medium">Medium (720p)</option>
                    <option value="high">High (1080p)</option>
                  </Select>
                </InputGroup>
                <InputGroup>
                  <Label>Voice Selection</Label>
                  <Select
                    value={settings.voice || 'male1'}
                    onChange={e => onSettingsChange('voice', e.target.value)}
                  >
                    <option value="male1">Male Voice 1</option>
                    <option value="male2">Male Voice 2</option>
                    <option value="female1">Female Voice 1</option>
                    <option value="female2">Female Voice 2</option>
                  </Select>
                </InputGroup>
                <InputGroup>
                  <Label>Voice Language</Label>
                  <Select
                    value={settings.voiceLanguage || 'en-US'}
                    onChange={e => onSettingsChange('voiceLanguage', e.target.value)}
                  >
                    <option value="en-US">English (US)</option>
                    <option value="en-GB">English (UK)</option>
                    <option value="vi-VN">Vietnamese</option>
                  </Select>
                </InputGroup>
                <InputGroup>
                  <Label>Speaking Rate ({settings.speakingRate || 1}x)</Label>
                  <Slider
                    min="0.5"
                    max="2"
                    step="0.1"
                    value={settings.speakingRate || 1}
                    onChange={e => onSettingsChange('speakingRate', e.target.value)}
                  />
                </InputGroup>
                <InputGroup>
                  <Label>Voice Pitch ({settings.voicePitch || 0})</Label>
                  <Slider
                    min="-20"
                    max="20"
                    step="1"
                    value={settings.voicePitch || 0}
                    onChange={e => onSettingsChange('voicePitch', e.target.value)}
                  />
                </InputGroup>
                <InputGroup>
                  <Label>Time per Slide (seconds)</Label>
                  <Input
                    type="number"
                    min="10"
                    max="300"
                    value={settings.slideTime || 30}
                    onChange={e => onSettingsChange('slideTime', e.target.value)}
                  />
                </InputGroup>
                <InputGroup>
                  <Label>Background Music</Label>
                  <Select
                    value={settings.backgroundMusic || 'none'}
                    onChange={e => onSettingsChange('backgroundMusic', e.target.value)}
                  >
                    <option value="none">None</option>
                    <option value="calm">Calm</option>
                    <option value="upbeat">Upbeat</option>
                    <option value="corporate">Corporate</option>
                  </Select>
                </InputGroup>
                <InputGroup>
                  <Label>Music Volume ({settings.musicVolume || 30}%)</Label>
                  <Slider
                    min="0"
                    max="100"
                    step="5"
                    value={settings.musicVolume || 30}
                    onChange={e => onSettingsChange('musicVolume', e.target.value)}
                  />
                </InputGroup>
              </SectionContent>
            </Section>
          )}

          {/* Quiz Generation Settings */}
          {activeFunction === 'quiz' && (
            <Section>
              <SectionHeader onClick={() => toggleSection('quizSettings')}>
                <SectionTitle>
                  <QuizIcon fontSize="small" />
                  Quiz Settings
                </SectionTitle>
                <ChevronRightIcon 
                  style={{ 
                    transform: isSectionExpanded('quizSettings') ? 'rotate(-90deg)' : 'rotate(90deg)',
                    transition: 'transform 0.3s ease'
                  }} 
                />
              </SectionHeader>
              <SectionContent isOpen={isSectionExpanded('quizSettings')}>
                <InputGroup>
                  <Label>Number of Questions</Label>
                  <Input
                    type="number"
                    min="1"
                    max="50"
                    value={settings.questionCount || 10}
                    onChange={e => onSettingsChange('questionCount', e.target.value)}
                  />
                </InputGroup>
                <InputGroup>
                  <Label>Time Limit per Question (seconds)</Label>
                  <Input
                    type="number"
                    min="30"
                    max="300"
                    value={settings.timePerQuestion || 60}
                    onChange={e => onSettingsChange('timePerQuestion', e.target.value)}
                  />
                </InputGroup>
                <InputGroup>
                  <Label>Difficulty Level</Label>
                  <Select
                    value={settings.difficulty || 'medium'}
                    onChange={e => onSettingsChange('difficulty', e.target.value)}
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </Select>
                </InputGroup>
                <InputGroup>
                  <Label>Topics to Focus</Label>
                  <Select
                    value={settings.topicFocus || 'all'}
                    onChange={e => onSettingsChange('topicFocus', e.target.value)}
                    multiple
                  >
                    <option value="all">All Topics</option>
                    <option value="key_concepts">Key Concepts</option>
                    <option value="definitions">Definitions</option>
                    <option value="examples">Examples</option>
                    <option value="applications">Applications</option>
                  </Select>
                </InputGroup>
                <InputGroup>
                  <Label>Question Types</Label>
                  <Select
                    value={settings.questionType || 'mixed'}
                    onChange={e => onSettingsChange('questionType', e.target.value)}
                  >
                    <option value="mixed">Mixed</option>
                    <option value="mcq">Multiple Choice Only</option>
                    <option value="truefalse">True/False Only</option>
                    <option value="openended">Open Ended Only</option>
                  </Select>
                </InputGroup>
                <InputGroup>
                  <Label>Include Explanations</Label>
                  <Select
                    value={settings.includeExplanations || 'correct'}
                    onChange={e => onSettingsChange('includeExplanations', e.target.value)}
                  >
                    <option value="none">No Explanations</option>
                    <option value="correct">Only for Correct Answers</option>
                    <option value="incorrect">Only for Incorrect Answers</option>
                    <option value="all">All Answers</option>
                  </Select>
                </InputGroup>
                <InputGroup>
                  <Label>Quiz Format</Label>
                  <Select
                    value={settings.quizFormat || 'standard'}
                    onChange={e => onSettingsChange('quizFormat', e.target.value)}
                  >
                    <option value="standard">Standard</option>
                    <option value="flashcard">Flashcards</option>
                    <option value="game">Game Mode</option>
                  </Select>
                </InputGroup>
              </SectionContent>
            </Section>
          )}
        </SettingsContainer>
      </SidebarContainer>
    </>
  );
};

export default RightSidebar; 