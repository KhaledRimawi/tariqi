import React, { useState } from 'react';
import { useDarkMode } from '../contexts/DarkModeContext';
import { Moon, Sun, Settings, Monitor } from 'lucide-react';
import './AdvancedDarkModeToggle.css';

const AdvancedDarkModeToggle = () => {
  const { isDarkMode, toggleDarkMode } = useDarkMode();
  const [showOptions, setShowOptions] = useState(false);

  const handleQuickToggle = () => {
    toggleDarkMode();
  };

  const handleSystemPreference = () => {
    const systemPrefersDark = window.matchMedia && 
      window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (systemPrefersDark !== isDarkMode) {
      toggleDarkMode();
    }
    setShowOptions(false);
  };

  const toggleOptions = () => {
    setShowOptions(!showOptions);
  };

  return (
    <div className="advanced-dark-mode-toggle">
      {/* Quick Toggle Button */}
      <button
        className="quick-toggle-btn"
        onClick={handleQuickToggle}
        aria-label={isDarkMode ? 'تفعيل الوضع العادي' : 'تفعيل الوضع المظلم'}
        title={isDarkMode ? 'تفعيل الوضع العادي' : 'تفعيل الوضع المظلم'}
      >
        {isDarkMode ? (
          <Sun size={20} className="toggle-icon" />
        ) : (
          <Moon size={20} className="toggle-icon" />
        )}
      </button>

      {/* Advanced Options Button */}
      <button
        className="options-btn"
        onClick={toggleOptions}
        aria-label="خيارات الوضع المظلم المتقدمة"
        title="خيارات متقدمة"
      >
        <Settings size={16} className="settings-icon" />
      </button>

      {/* Options Dropdown */}
      {showOptions && (
        <div className="options-dropdown">
          <div className="dropdown-header">
            <span>إعدادات العرض</span>
          </div>
          
          <button
            className={`option-item ${!isDarkMode ? 'active' : ''}`}
            onClick={() => {
              if (isDarkMode) toggleDarkMode();
              setShowOptions(false);
            }}
          >
            <Sun size={16} />
            <span>الوضع العادي</span>
          </button>

          <button
            className={`option-item ${isDarkMode ? 'active' : ''}`}
            onClick={() => {
              if (!isDarkMode) toggleDarkMode();
              setShowOptions(false);
            }}
          >
            <Moon size={16} />
            <span>الوضع المظلم</span>
          </button>

          <button
            className="option-item"
            onClick={handleSystemPreference}
          >
            <Monitor size={16} />
            <span>حسب النظام</span>
          </button>
        </div>
      )}

      {/* Overlay to close dropdown */}
      {showOptions && (
        <div 
          className="dropdown-overlay" 
          onClick={() => setShowOptions(false)}
        />
      )}
    </div>
  );
};

export default AdvancedDarkModeToggle;
