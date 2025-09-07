import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { DarkModeProvider, useDarkMode } from '../contexts/DarkModeContext';
import DarkModeToggle from '../components/DarkModeToggle';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Test component to use the hook
const TestComponent = () => {
  const { isDarkMode, toggleDarkMode } = useDarkMode();
  return (
    <div>
      <span data-testid="dark-mode-status">
        {isDarkMode ? 'dark' : 'light'}
      </span>
      <button onClick={toggleDarkMode} data-testid="toggle-button">
        Toggle
      </button>
    </div>
  );
};

describe('Dark Mode Context', () => {
  beforeEach(() => {
    localStorageMock.getItem.mockClear();
    localStorageMock.setItem.mockClear();
    document.body.classList.remove('dark-mode');
  });

  test('should initialize with light mode by default', () => {
    localStorageMock.getItem.mockReturnValue(null);
    
    render(
      <DarkModeProvider>
        <TestComponent />
      </DarkModeProvider>
    );

    expect(screen.getByTestId('dark-mode-status')).toHaveTextContent('light');
  });

  test('should initialize with dark mode from localStorage', () => {
    localStorageMock.getItem.mockReturnValue('true');
    
    render(
      <DarkModeProvider>
        <TestComponent />
      </DarkModeProvider>
    );

    expect(screen.getByTestId('dark-mode-status')).toHaveTextContent('dark');
    expect(document.body.classList.contains('dark-mode')).toBe(true);
  });

  test('should toggle dark mode', () => {
    localStorageMock.getItem.mockReturnValue('false');
    
    render(
      <DarkModeProvider>
        <TestComponent />
      </DarkModeProvider>
    );

    const toggleButton = screen.getByTestId('toggle-button');
    const statusElement = screen.getByTestId('dark-mode-status');

    expect(statusElement).toHaveTextContent('light');

    fireEvent.click(toggleButton);

    expect(statusElement).toHaveTextContent('dark');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('darkMode', 'true');
    expect(document.body.classList.contains('dark-mode')).toBe(true);
  });

  test('should save preference to localStorage', () => {
    localStorageMock.getItem.mockReturnValue('false');
    
    render(
      <DarkModeProvider>
        <TestComponent />
      </DarkModeProvider>
    );

    const toggleButton = screen.getByTestId('toggle-button');

    fireEvent.click(toggleButton);

    expect(localStorageMock.setItem).toHaveBeenCalledWith('darkMode', 'true');
  });
});

describe('Dark Mode Toggle Component', () => {
  test('should render toggle button', () => {
    render(
      <DarkModeProvider>
        <DarkModeToggle />
      </DarkModeProvider>
    );

    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
  });

  test('should show correct icon for current mode', () => {
    localStorageMock.getItem.mockReturnValue('false');
    
    render(
      <DarkModeProvider>
        <DarkModeToggle />
      </DarkModeProvider>
    );

    // Should show moon icon in light mode
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('title', 'تفعيل الوضع المظلم');
  });

  test('should toggle mode when clicked', () => {
    localStorageMock.getItem.mockReturnValue('false');
    
    render(
      <DarkModeProvider>
        <DarkModeToggle />
      </DarkModeProvider>
    );

    const button = screen.getByRole('button');
    
    fireEvent.click(button);

    expect(document.body.classList.contains('dark-mode')).toBe(true);
    expect(button).toHaveAttribute('title', 'تفعيل الوضع العادي');
  });
});
