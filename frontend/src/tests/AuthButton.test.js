import React from 'react';
import { render, screen } from '@testing-library/react';
import { PublicClientApplication } from '@azure/msal-browser';
import { MsalProvider } from '@azure/msal-react';
import AuthButton from '../pages/AuthButton';

// Mock MSAL configuration
const mockMsalConfig = {
  auth: {
    clientId: 'test-client-id',
    authority: 'https://login.microsoftonline.com/common',
    redirectUri: 'http://localhost:3000'
  }
};

const mockPca = new PublicClientApplication(mockMsalConfig);

// Mock account
const mockAccount = {
  homeAccountId: 'test-home-account-id',
  environment: 'login.windows.net',
  tenantId: 'test-tenant-id',
  username: 'test@example.com',
  name: 'Test User'
};

describe('AuthButton Component', () => {
  test('renders sign in button when not authenticated', () => {
    render(
      <MsalProvider instance={mockPca}>
        <AuthButton />
      </MsalProvider>
    );

    expect(screen.getByText('Sign In')).toBeInTheDocument();
  });

  test('renders user badge and sign out button when authenticated', () => {
    // Mock active account
    jest.spyOn(mockPca, 'getActiveAccount').mockReturnValue(mockAccount);

    render(
      <MsalProvider instance={mockPca}>
        <AuthButton />
      </MsalProvider>
    );

    expect(screen.getByText('Hello, Test User!')).toBeInTheDocument();
    expect(screen.getByText('Sign Out')).toBeInTheDocument();
    expect(screen.getByText('T')).toBeInTheDocument(); // Avatar
  });

  test('displays correct avatar initial', () => {
    jest.spyOn(mockPca, 'getActiveAccount').mockReturnValue(mockAccount);

    render(
      <MsalProvider instance={mockPca}>
        <AuthButton />
      </MsalProvider>
    );

    const avatar = screen.getByText('T');
    expect(avatar).toHaveClass('avatar');
  });
});
