/**
 * SecureRedLab - Terminal Component
 * Phase 8.4 - Interactive Terminal Emulator with xterm.js
 */

import { useEffect, useRef } from 'react';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { WebLinksAddon } from 'xterm-addon-web-links';
import 'xterm/css/xterm.css';

interface TerminalProps {
  className?: string;
  initialMessage?: string;
  onCommand?: (command: string) => void;
}

export default function TerminalComponent({ 
  className = '', 
  initialMessage = 'Welcome to SecureRedLab Terminal\r\n',
  onCommand 
}: TerminalProps) {
  const terminalRef = useRef<HTMLDivElement>(null);
  const xtermRef = useRef<Terminal | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const commandBufferRef = useRef<string>('');

  useEffect(() => {
    if (!terminalRef.current || xtermRef.current) return;

    // Create terminal instance
    const terminal = new Terminal({
      cursorBlink: true,
      fontSize: 14,
      fontFamily: 'JetBrains Mono, monospace',
      theme: {
        background: '#1e1e1e',
        foreground: '#d4d4d4',
        cursor: '#00ff00',
        cursorAccent: '#1e1e1e',
        selectionBackground: '#264f78',
        black: '#000000',
        red: '#cd3131',
        green: '#0dbc79',
        yellow: '#e5e510',
        blue: '#2472c8',
        magenta: '#bc3fbc',
        cyan: '#11a8cd',
        white: '#e5e5e5',
        brightBlack: '#666666',
        brightRed: '#f14c4c',
        brightGreen: '#23d18b',
        brightYellow: '#f5f543',
        brightBlue: '#3b8eea',
        brightMagenta: '#d670d6',
        brightCyan: '#29b8db',
        brightWhite: '#e5e5e5',
      },
      allowTransparency: true,
      scrollback: 1000,
    });

    // Add addons
    const fitAddon = new FitAddon();
    const webLinksAddon = new WebLinksAddon();
    
    terminal.loadAddon(fitAddon);
    terminal.loadAddon(webLinksAddon);

    // Open terminal
    terminal.open(terminalRef.current);
    fitAddon.fit();

    // Store refs
    xtermRef.current = terminal;
    fitAddonRef.current = fitAddon;

    // Write initial message
    terminal.writeln(initialMessage);
    terminal.writeln('Type "help" for available commands\r\n');
    writePrompt(terminal);

    // Handle input
    terminal.onData((data) => {
      const code = data.charCodeAt(0);

      // Handle printable characters
      if (code >= 32 && code < 127) {
        commandBufferRef.current += data;
        terminal.write(data);
      }
      // Handle backspace
      else if (code === 127) {
        if (commandBufferRef.current.length > 0) {
          commandBufferRef.current = commandBufferRef.current.slice(0, -1);
          terminal.write('\b \b');
        }
      }
      // Handle enter
      else if (code === 13) {
        const command = commandBufferRef.current.trim();
        terminal.write('\r\n');
        
        if (command) {
          handleCommand(terminal, command, onCommand);
        }
        
        commandBufferRef.current = '';
        writePrompt(terminal);
      }
      // Handle Ctrl+C
      else if (code === 3) {
        terminal.write('^C\r\n');
        commandBufferRef.current = '';
        writePrompt(terminal);
      }
    });

    // Handle resize
    const handleResize = () => {
      fitAddon.fit();
    };
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      terminal.dispose();
    };
  }, [initialMessage, onCommand]);

  return (
    <div className={`terminal-container ${className}`}>
      <div ref={terminalRef} className="w-full h-full" />
    </div>
  );
}

// Helper: Write prompt
function writePrompt(terminal: Terminal) {
  terminal.write('\r\n\x1b[32mroot@secureredlab\x1b[0m:\x1b[34m~\x1b[0m$ ');
}

// Helper: Handle commands
function handleCommand(terminal: Terminal, command: string, onCommand?: (cmd: string) => void) {
  const parts = command.split(' ');
  const cmd = parts[0].toLowerCase();
  const args = parts.slice(1);

  // Call external handler if provided
  if (onCommand) {
    onCommand(command);
  }

  // Built-in commands
  switch (cmd) {
    case 'help':
      terminal.writeln('Available commands:');
      terminal.writeln('  help              - Show this help message');
      terminal.writeln('  clear             - Clear terminal');
      terminal.writeln('  scan <target>     - Start a security scan');
      terminal.writeln('  attack <target>   - Launch an attack');
      terminal.writeln('  status            - Show system status');
      terminal.writeln('  whoami            - Show current user');
      terminal.writeln('  exit              - Exit terminal');
      break;

    case 'clear':
      terminal.clear();
      break;

    case 'scan':
      if (args.length === 0) {
        terminal.writeln('\x1b[31mError:\x1b[0m Target required. Usage: scan <target>');
      } else {
        terminal.writeln(`\x1b[32m[*]\x1b[0m Starting scan on ${args[0]}...`);
        terminal.writeln(`\x1b[32m[*]\x1b[0m Scan initiated. ID: scan-${Date.now()}`);
      }
      break;

    case 'attack':
      if (args.length === 0) {
        terminal.writeln('\x1b[31mError:\x1b[0m Target required. Usage: attack <target>');
      } else {
        terminal.writeln(`\x1b[33m[!]\x1b[0m Launching attack on ${args[0]}...`);
        terminal.writeln(`\x1b[33m[!]\x1b[0m Attack initiated. ID: attack-${Date.now()}`);
      }
      break;

    case 'status':
      terminal.writeln('System Status:');
      terminal.writeln('  Backend:  \x1b[32m✓ Online\x1b[0m');
      terminal.writeln('  Database: \x1b[32m✓ Connected\x1b[0m');
      terminal.writeln('  AI Core:  \x1b[32m✓ Ready\x1b[0m');
      terminal.writeln('  Memory:   \x1b[33m78%\x1b[0m');
      terminal.writeln('  CPU:      \x1b[32m23%\x1b[0m');
      break;

    case 'whoami':
      terminal.writeln('root');
      break;

    case 'exit':
      terminal.writeln('Goodbye!');
      break;

    case '':
      // Empty command, do nothing
      break;

    default:
      terminal.writeln(`\x1b[31mCommand not found:\x1b[0m ${cmd}`);
      terminal.writeln('Type "help" for available commands');
  }
}
