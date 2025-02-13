import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import styled from 'styled-components';

const NavContainer = styled.nav`
  background-color: #1a237e;
  padding: 16px 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const NavList = styled.ul`
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  gap: 24px;
`;

const NavItem = styled.li`
  a {
    color: white;
    text-decoration: none;
    font-size: 16px;
    font-weight: ${props => props.active ? '600' : '400'};
    padding: 8px 16px;
    border-radius: 4px;
    transition: background-color 0.3s;

    &:hover {
      background-color: #283593;
    }
  }
`;

const Navigation = () => {
  const location = useLocation();

  return (
    <NavContainer>
      <NavList>
        <NavItem active={location.pathname === '/'}>
          <Link to="/">AI Tutor Chat</Link>
        </NavItem>
        <NavItem active={location.pathname === '/slide-converter'}>
          <Link to="/slide-converter">Slide to Video</Link>
        </NavItem>
        <NavItem active={location.pathname === '/quiz-generator'}>
          <Link to="/quiz-generator">Quiz Generator</Link>
        </NavItem>
      </NavList>
    </NavContainer>
  );
};

export default Navigation; 