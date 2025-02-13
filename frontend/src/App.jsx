import React from "react";
import ChatPage from "./pages/ChatPage";
import styled from "styled-components";

const AppContainer = styled.div`
  height: 100%;
  display: flex;
  flex-direction: column;
`;

/**
 * Component gốc của ứng dụng
 * Render trang ChatPage làm trang chính
 */
function App() {
  return (
    <AppContainer>
      <ChatPage />
    </AppContainer>
  );
}

export default App;
