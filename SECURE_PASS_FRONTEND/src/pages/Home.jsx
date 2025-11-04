import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import styled, { keyframes } from 'styled-components';
import sciFiLogo from '../assets/sci-fi-logo.png';

// Floating animation keyframes
const float = keyframes`
  0% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
  100% { transform: translateY(0); }
`;

// Styled Components
const PageWrapper = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0d0d1a, #1a1a33);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  padding: 2rem;
`;

const Card = styled.div`
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 2.5rem;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  color: #e0e0e0;
  text-align: center;
`;

const Logo = styled.img`
  width: 120px;
  margin-bottom: 1.5rem;
  animation: ${float} 6s ease-in-out infinite;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: #00d9a6;
`;

const Subtitle = styled.p`
  font-size: 1.1rem;
  color: #a0a8b7;
  margin-bottom: 2rem;
  line-height: 1.6;
`;

const NavigationGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin: 2rem 0;
`;

const NavButton = styled(Link)`
  padding: 1rem;
  background: rgba(0, 217, 166, 0.1);
  border: 1px solid rgba(0, 217, 166, 0.3);
  border-radius: 12px;
  text-decoration: none;
  color: #00d9a6;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  
  &:hover {
    background: rgba(0, 217, 166, 0.2);
    border-color: #00d9a6;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 217, 166, 0.2);
  }
  
  .icon {
    font-size: 1.5rem;
    margin-bottom: 0.25rem;
  }
  
  .title {
    font-size: 1rem;
    font-weight: 600;
  }
  
  .desc {
    font-size: 0.75rem;
    color: #a0a8b7;
    font-weight: 400;
  }
`;

const AuthButtons = styled.div`
  display: flex;
  gap: 1rem;
  margin: 2rem 0;
  justify-content: center;
`;

const AuthButton = styled(Link)`
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #00d9a6, #00c096);
  color: #0d0d1a;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  font-size: 1rem;
  
  &:hover {
    background: linear-gradient(135deg, #00c096, #00d9a6);
    transform: translateY(-1px);
  }
  
  &.secondary {
    background: transparent;
    border: 1px solid #00d9a6;
    color: #00d9a6;
    
    &:hover {
      background: rgba(0, 217, 166, 0.1);
    }
  }
`;

const DemoCredentials = styled.div`
  margin-top: 2rem;
  padding: 1.5rem;
  background: rgba(0, 217, 166, 0.1);
  border: 1px solid rgba(0, 217, 166, 0.2);
  border-radius: 12px;
  text-align: left;
  
  h3 {
    color: #00d9a6;
    font-weight: 600;
    margin-bottom: 1rem;
    font-size: 1rem;
    text-align: center;
  }
  
  .credential-grid {
    display: grid;
    gap: 0.75rem;
  }
  
  p {
    margin: 0;
    font-size: 0.9rem;
    color: #e0e0e0;
    padding: 0.5rem;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 6px;
    
    strong {
      color: #00d9a6;
      min-width: 80px;
      display: inline-block;
    }
  }
`;

function Home() {
  const navigate = useNavigate();

  return (
    <PageWrapper>
      <Card>
        <Logo src={sciFiLogo} alt="Secure Pass Logo" />
        <Title>Secure Pass</Title>
        <Subtitle>
          Advanced Vehicle Security & Access Control System
          <br />
          Choose your access level or explore the demo
        </Subtitle>

        <AuthButtons>
          <AuthButton to="/login">Login</AuthButton>
          <AuthButton to="/register" className="secondary">Register</AuthButton>
        </AuthButtons>

        <NavigationGrid>
          <NavButton to="/admin">
            <div className="icon">👨‍💼</div>
            <div className="title">Admin Dashboard</div>
            <div className="desc">System Management</div>
          </NavButton>
          
          <NavButton to="/manager">
            <div className="icon">📊</div>
            <div className="title">Manager Dashboard</div>
            <div className="desc">Operations Control</div>
          </NavButton>
          
          <NavButton to="/security">
            <div className="icon">🔒</div>
            <div className="title">Security Dashboard</div>
            <div className="desc">Access Monitoring</div>
          </NavButton>
          
          <NavButton to="/test">
            <div className="icon">🧪</div>
            <div className="title">Test Page</div>
            <div className="desc">Demo Features</div>
          </NavButton>
        </NavigationGrid>

        <DemoCredentials>
          <h3>Demo Access Credentials</h3>
          <div className="credential-grid">
            <p><strong>Admin:</strong> admin / admin123</p>
            <p><strong>Manager:</strong> manager / manager123</p>
            <p><strong>Security:</strong> security / security123</p>
          </div>
        </DemoCredentials>
      </Card>
    </PageWrapper>
  );
}

export default Home;