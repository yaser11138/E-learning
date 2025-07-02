import React, { useState, useEffect, useRef } from 'react';
import './Chat.css';

const Chat = ({ roomName = "general" }) => {
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [socket, setSocket] = useState(null);
    const [socketConnected, setSocketConnected] = useState(false);
    const [error, setError] = useState(null);
    const messagesEndRef = useRef(null);

    const loggedInUser = JSON.parse(localStorage.getItem('user')); // Basic way to get user info

    useEffect(() => {
        // Determine WebSocket protocol
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        // Construct WebSocket URL
        // Assuming your Django backend runs on port 8000 locally for WebSocket connections
        // Adjust the host and port if your backend (especially Daphne) runs elsewhere
        const wsUrl = `${wsProtocol}//${window.location.hostname}:8000/ws/chat/${roomName}/`;

        console.log(`Attempting to connect to WebSocket: ${wsUrl}`);
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('WebSocket connected');
            setSocketConnected(true);
            setError(null);
            // Optionally send an auth token if your backend requires it via WebSocket
            // For example, if you're not relying solely on session/cookie auth from AuthMiddlewareStack
            // if (loggedInUser && loggedInUser.token) {
            //     ws.send(JSON.stringify({ token: loggedInUser.token }));
            // }
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Received message:', data);
            setMessages(prevMessages => [...prevMessages, data]);
        };

        ws.onerror = (err) => {
            console.error('WebSocket error:', err);
            setError(`WebSocket error. Check console for details. Ensure backend WebSocket server is running at ${wsUrl}.`);
            setSocketConnected(false);
        };

        ws.onclose = (event) => {
            console.log('WebSocket disconnected:', event);
            setSocketConnected(false);
            if (!event.wasClean) {
                setError(`WebSocket connection died unexpectedly. Code: ${event.code}, Reason: ${event.reason || 'No reason given'}. Attempting to reconnect might be needed.`);
            }
        };

        setSocket(ws);

        return () => {
            if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
                ws.close();
            }
        };
    }, [roomName]); // Reconnect if roomName changes

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleSendMessage = (e) => {
        e.preventDefault();
        if (newMessage.trim() && socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ message: newMessage }));
            setNewMessage('');
        } else {
            console.warn('Cannot send message: Socket not open or message empty.');
            if (!socket || socket.readyState !== WebSocket.OPEN) {
                setError("Cannot send message: WebSocket is not connected.");
            }
        }
    };

    if (!loggedInUser) {
        return <div className="chat-container"><p>Please log in to use the chat.</p></div>;
    }

    return (
        <div className="chat-container">
            <h2>Chat Room: {roomName}</h2>
            {error && <p className="chat-error">{error}</p>}
            {!socketConnected && !error && <p>Connecting to chat...</p>}
            {socketConnected && <p className="chat-status">Connected</p>}

            <div className="messages-area">
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={`message ${msg.sender_username === loggedInUser.username ? 'sent' : 'received'}`}
                    >
                        <strong className="message-sender">{msg.sender_username || 'Anonymous'}:</strong>
                        <p className="message-content">{msg.message}</p>
                        <span className="message-timestamp">{new Date(msg.timestamp).toLocaleTimeString()}</span>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>
            <form onSubmit={handleSendMessage} className="message-input-form">
                <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Type your message..."
                    disabled={!socketConnected}
                />
                <button type="submit" disabled={!socketConnected}>Send</button>
            </form>
        </div>
    );
};

export default Chat;
