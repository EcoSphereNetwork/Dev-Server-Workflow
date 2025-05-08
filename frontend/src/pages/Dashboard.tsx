// src/pages/Dashboard.tsx
import React from 'react';
import { Dashboard as DashboardComponent } from '../components/Dashboard';
import { Container } from '../design-system';

const Dashboard: React.FC = () => {
  return (
    <Container size="xl">
      <DashboardComponent />
    </Container>
  );
};

export default Dashboard;