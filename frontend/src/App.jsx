import React from "react";
import ChatPage from "./pages/ChatPage";
import styled, { createGlobalStyle } from "styled-components";
import Profile from './pages/Profile';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  html, body, #root {
    height: 100%;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Icons", "Helvetica Neue", Helvetica, Arial, sans-serif;
  }

  body {
    background-color: #f5f5f7;
    color: #1d1d1f;
    line-height: 1.47059;
    letter-spacing: -0.022em;
  }

  :root {
    --primary-color: #0066CC;
    --secondary-color: #06c;
    --success-color: #34c759;
    --warning-color: #ff9f0a;
    --error-color: #ff3b30;
    --text-primary: #1d1d1f;
    --text-secondary: #86868b;
    --background-primary: #ffffff;
    --background-secondary: #f5f5f7;
    --border-color: rgba(0, 0, 0, 0.1);
    --blur-background: rgba(255, 255, 255, 0.72);
  }
`;

const AppContainer = styled.div`
  height: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, var(--background-primary) 0%, var(--background-secondary) 100%);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
`;

/**
 * Component gốc của ứng dụng
 * Render trang ChatPage làm trang chính
 */
function App() {
  return (
    <Router>
      <GlobalStyle />
      <AppContainer>
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </AppContainer>
    </Router>
  );
}

export default App;
