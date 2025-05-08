// src/pages/Login.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import Card from '../components/common/Card';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import Alert from '../components/common/Alert';
import useAuthStore from '../store/auth';
import apiClient from '../api/client';
import { colors } from '../theme';

const LoginContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: ${colors.background.default};
`;

const LoginCard = styled(Card)`
  width: 100%;
  max-width: 400px;
  padding: 24px;
`;

const LoginTitle = styled.h1`
  font-size: 1.5rem;
  text-align: center;
  margin-bottom: 24px;
  color: ${colors.primary.main};
`;

const LoginForm = styled.form`
  display: flex;
  flex-direction: column;
`;

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { login, isLoading, setLoading } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      // In einer realen Anwendung würde hier ein API-Aufruf erfolgen
      const response = await apiClient.post('/auth/login', { username, password });
      login(response.data.token, response.data.user);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Anmeldung fehlgeschlagen. Bitte überprüfen Sie Ihre Anmeldedaten.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <LoginContainer>
      <LoginCard>
        <LoginTitle>Dev-Server-Workflow</LoginTitle>
        
        {error && (
          <Alert variant="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        )}
        
        <LoginForm onSubmit={handleSubmit}>
          <Input
            label="Benutzername"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            fullWidth
            required
          />
          
          <Input
            label="Passwort"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            fullWidth
            required
          />
          
          <Button
            type="submit"
            variant="primary"
            fullWidth
            loading={isLoading}
            disabled={isLoading}
            style={{ marginTop: '16px' }}
          >
            Anmelden
          </Button>
        </LoginForm>
      </LoginCard>
    </LoginContainer>
  );
};

export default Login;