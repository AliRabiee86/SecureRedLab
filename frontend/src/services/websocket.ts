/**
 * SecureRedLab - WebSocket Client
 * Phase 8.3 - Real-time Updates
 */

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

interface WebSocketMessage {
  type: WebSocketEventType;
  data: any;
  timestamp: string;
}

type EventHandler = (data: any) => void;

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;
  private eventHandlers: Map<WebSocketEventType, EventHandler[]> = new Map();
  private isIntentionallyClosed = false;

  constructor(url?: string) {
    const wsUrl = url || import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
    this.url = wsUrl;
    console.log('🔌 WebSocket Client initialized with URL:', this.url);
  }

  /**
   * Connect to WebSocket server
   */
  public connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('⚠️ WebSocket already connected');
      return;
    }

    try {
      console.log('🔌 Connecting to WebSocket...');
      this.ws = new WebSocket(this.url);

      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onerror = this.handleError.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
    } catch (error) {
      console.error('❌ WebSocket connection error:', error);
      this.scheduleReconnect();
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  public disconnect(): void {
    console.log('🔌 Disconnecting from WebSocket...');
    this.isIntentionallyClosed = true;
    this.ws?.close();
    this.ws = null;
  }

  /**
   * Send message to server
   */
  public send(message: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      const payload = typeof message === 'string' ? message : JSON.stringify(message);
      this.ws.send(payload);
      console.log('📤 Sent message:', payload);
    } else {
      console.warn('⚠️ WebSocket not connected. Cannot send message.');
    }
  }

  /**
   * Subscribe to event
   */
  public on(event: WebSocketEventType, handler: EventHandler): () => void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, []);
    }
    this.eventHandlers.get(event)!.push(handler);

    // Return unsubscribe function
    return () => this.off(event, handler);
  }

  /**
   * Unsubscribe from event
   */
  public off(event: WebSocketEventType, handler: EventHandler): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  /**
   * Get connection status
   */
  public isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * Handle WebSocket open event
   */
  private handleOpen(): void {
    console.log('✅ WebSocket connected');
    this.reconnectAttempts = 0;
    this.emit('connection.established', { connected: true });
  }

  /**
   * Handle WebSocket message event
   */
  private handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      console.log('📥 Received message:', message);
      this.emit(message.type, message.data);
    } catch (error) {
      console.error('❌ Error parsing WebSocket message:', error);
    }
  }

  /**
   * Handle WebSocket error event
   */
  private handleError(error: Event): void {
    console.error('❌ WebSocket error:', error);
  }

  /**
   * Handle WebSocket close event
   */
  private handleClose(): void {
    console.log('🔌 WebSocket closed');
    this.emit('connection.closed', { connected: false });

    if (!this.isIntentionallyClosed) {
      this.scheduleReconnect();
    }
  }

  /**
   * Schedule reconnection attempt
   */
  private scheduleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(
        `🔄 Reconnecting in ${this.reconnectDelay / 1000}s (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`
      );
      setTimeout(() => this.connect(), this.reconnectDelay);
    } else {
      console.error('❌ Max reconnection attempts reached. Giving up.');
    }
  }

  /**
   * Emit event to registered handlers
   */
  private emit(event: WebSocketEventType, data: any): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.forEach((handler) => {
        try {
          handler(data);
        } catch (error) {
          console.error(`❌ Error in event handler for '${event}':`, error);
        }
      });
    }
  }
}

// Singleton instance
let wsClient: WebSocketClient | null = null;

/**
 * Get WebSocket client instance
 */
export function getWebSocketClient(): WebSocketClient {
  if (!wsClient) {
    wsClient = new WebSocketClient();
  }
  return wsClient;
}

/**
 * Initialize WebSocket connection
 */
export function initWebSocket(): WebSocketClient {
  const client = getWebSocketClient();
  client.connect();
  return client;
}
