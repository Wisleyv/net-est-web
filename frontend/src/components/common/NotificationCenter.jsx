/**
 * Global Notification System
 * Centralized toast/notification component
 */

import React, { useEffect } from 'react';
import { X, CheckCircle, AlertTriangle, AlertCircle, Info } from 'lucide-react';
import useAppStore from '../../stores/useAppStore';

const NotificationCenter = () => {
  const { notifications, removeNotification } = useAppStore();

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'success': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error': return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'warning': return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'info': return <Info className="w-5 h-5 text-blue-500" />;
      default: return <Info className="w-5 h-5 text-gray-500" />;
    }
  };

  const getNotificationStyles = (type) => {
    const baseStyles = "border-l-4 bg-white shadow-lg rounded-lg p-4 mb-3 max-w-md";
    
    switch (type) {
      case 'success': return `${baseStyles} border-green-500`;
      case 'error': return `${baseStyles} border-red-500`;
      case 'warning': return `${baseStyles} border-yellow-500`;
      case 'info': return `${baseStyles} border-blue-500`;
      default: return `${baseStyles} border-gray-500`;
    }
  };

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {notifications.map((notification) => (
        <NotificationItem
          key={notification.id}
          notification={notification}
          onRemove={removeNotification}
          getIcon={getNotificationIcon}
          getStyles={getNotificationStyles}
        />
      ))}
    </div>
  );
};

const NotificationItem = ({ notification, onRemove, getIcon, getStyles }) => {
  const { id, type, title, message, duration = 5000, persistent = false } = notification;

  useEffect(() => {
    if (!persistent && duration > 0) {
      const timer = setTimeout(() => {
        onRemove(id);
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [id, duration, persistent, onRemove]);

  return (
    <div className={getStyles(type)}>
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">
          {getIcon(type)}
        </div>
        
        <div className="flex-1 min-w-0">
          {title && (
            <h4 className="text-sm font-semibold text-gray-900 mb-1">
              {title}
            </h4>
          )}
          
          <p className="text-sm text-gray-700">
            {message}
          </p>
        </div>
        
        <button
          onClick={() => onRemove(id)}
          className="flex-shrink-0 ml-2 text-gray-400 hover:text-gray-600 transition-colors"
          aria-label="Fechar notificação"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default NotificationCenter;
