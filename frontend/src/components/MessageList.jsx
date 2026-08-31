function MessageList({ messages, loading }) {
  if (messages.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">?</div>
        <h2>Comment puis-je vous aider ?</h2>
        <p>
          Posez une question sur votre compte ou demandez une
          action sur un ticket.
        </p>
      </div>
    );
  }

  return (
    <div className="message-list" aria-live="polite">
      {messages.map((message) => (
        <article
          className={`message message-${message.role}`}
          key={message.id}
        >
          <span className="message-author">
            {message.role === "user" ? "Vous" : "Copilot"}
          </span>
          <p>{message.content}</p>
        </article>
      ))}

      {loading && (
        <div className="typing-indicator" aria-label="Réponse en cours">
          <span />
          <span />
          <span />
        </div>
      )}
    </div>
  );
}

export default MessageList;
