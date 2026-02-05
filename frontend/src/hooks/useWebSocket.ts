/**
 * SecureRedLab - WebSocket React Hook
 * Phase 8.3 - Real-time Updates
 */

import { useEffect, useState, useCallback } from 'react';
import { getWebSocketClient } from '../services/websocket';

type WebSocketEventType =
  | 'connection.established'
  | 'connection.closed'
  | 'scan.started'
  | 'scan.progress'
  | 'scan.completed'
  | 'scan.failed'
  | 'attack.started'
  | 'attack.progress'
  | 'attack.completed'
  | 'attack.failed'
  | 'vulnerability.discovered'
  | 'notification'
  | 'message.received';

interface UseWebSocketOptions {
  autoConnect?: boolean;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: any) => void;
}

/**
 * Custom hook for WebSocket functionality
 */
export function useWebSocket(options: UseWebSocketOptions = {}) {
  const { autoConnect = true, onConnect, onDisconnect, onError } = options;
  
  const [isConnected, setIsConnected] = useState(false);
  const wsClient = getWebSocketClient();

  useEffect(() => {
    // Subscribe to connection events
    const unsubscribeConnect = wsClient.on('connection.established', () => {
      console.log('✅ WebSocket connected (hook)');
      setIsConnected(true);
      onConnect?.();
    });

    const unsubscribeDisconnect = wsClient.on('connection.closed', () => {
      console.log('🔌 WebSocket disconnected (hook)');
      setIsConnected(false);
      onDisconnect?.();
    });

    // Auto-connect if enabled
    if (autoConnect && !wsClient.isConnected()) {
      wsClient.connect();
    }

    // Cleanup on unmount
    return () => {
      unsubscribeConnect();
      unsubscribeDisconnect();
    };
  }, [autoConnect, onConnect, onDisconnect, wsClient]);

  /**
   * Subscribe to WebSocket event
   */
  const subscribe = useCallback(
    (event: WebSocketEventType, handler: (data: any) => void) => {
      return wsClient.on(event, handler);
    },
    [wsClient]
  );

  /**
   * Send message via WebSocket
   */
  const send = useCallback(
    (message: any) => {
      wsClient.send(message);
    },
    [wsClient]
  );

  /**
   * Connect to WebSocket
   */
  const connect = useCallback(() => {
    wsClient.connect();
  }, [wsClient]);

  /**
   * Disconnect from WebSocket
   */
  const disconnect = useCallback(() => {
    wsClient.disconnect();
  }, [wsClient]);

  return {
    isConnected,
    subscribe,
    send,
    connect,
    disconnect,
  };
}

/**
 * Hook for subscribing to specific WebSocket event
 */
export function useWebSocketEvent(
  event: WebSocketEventType,
  handler: (data: any) => void,
  deps: any[] = []
) {
  const wsClient = getWebSocketClient();

  useEffect(() => {
    const unsubscribe = wsClient.on(event, handler);
    return unsubscribe;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [event, ...deps]);
}
