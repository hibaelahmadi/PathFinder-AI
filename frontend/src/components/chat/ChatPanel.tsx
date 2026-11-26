
function ChatPanel() {
    return (
        <section className="panel chat-panel">
            <div className="panel-heading">
                <div>
                    <h2>AI Orientation Assistant</h2>
                    <p>Let's discover your academic options together.</p>
                </div>
                <span className="online-indicator">● Online</span>
            </div>

            <div className="chat-content">
                <div className="assistant-message">
                    <div className="assistant-avatar">AI</div>
                    <div className="message-bubble">
                        <strong>Hello! 👋</strong>
                        <p>
                            Welcome to PathFinder AI. I'm here to help you
                            explore higher education opportunities in Morocco.
                        </p>
                        <p>
                            To get started, tell me about your Baccalaureate
                            series and what subjects interest you.
                        </p>
                    </div>
                </div>
            </div>

            <div className="chat-composer">
                <input
                    type="text"
                    placeholder="Type your message..."
                    aria-label="Type your message"
                />
                <button type="button" aria-label="Send message">
                    ➤
                </button>
            </div>

            <p className="chat-disclaimer">
                AI-generated guidance should be checked against official sources.
            </p>
        </section>
    )
}

export default ChatPanel
