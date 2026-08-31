import { useState } from "react";

import ChatInput from "./components/ChatInput";
import MessageList from "./components/MessageList";
import ReviewPanel from "./components/ReviewPanel";
import { reviewAction, sendMessage } from "./services/supportApi";
import "./App.css";

function createMessage(role, content) {
  return {
    id: crypto.randomUUID(),
    role,
    content,
  };
}

function App() {
  const [messages, setMessages] = useState([]);
  const [threadId, setThreadId] = useState(null);
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSend(question) {
    setMessages((currentMessages) => [
      ...currentMessages,
      createMessage("user", question),
    ]);
    setLoading(true);
    setError(null);

    try {
      const result = await sendMessage(question, threadId);

      setThreadId(result.thread_id);
      setReview(
        result.status === "review_required" ? result.review : null,
      );

      if (result.answer) {
        setMessages((currentMessages) => [
          ...currentMessages,
          createMessage("assistant", result.answer),
        ]);
      }
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleReview(decision) {
    setLoading(true);
    setError(null);

    try {
      const result = await reviewAction(threadId, decision);

      setReview(null);

      if (result.answer) {
        setMessages((currentMessages) => [
          ...currentMessages,
          createMessage("assistant", result.answer),
        ]);
      }
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  const status = review
    ? "Validation requise"
    : loading
      ? "Agent en réflexion"
      : "Agent disponible";

  return (
    <main className="app">
      <section className="chat-card">
        <header className="chat-header">
          <div className="brand">
            <div className="logo">SC</div>
            <div>
              <h1>Support Copilot</h1>
              <p>Agent IA de support technique</p>
            </div>
          </div>

          <div className="agent-status">
            <span className="status-dot" />
            {status}
          </div>
        </header>

        <MessageList messages={messages} loading={loading} />

        {error && (
          <div className="error-message" role="alert">
            {error}
          </div>
        )}

        <ReviewPanel
          review={review}
          onDecision={handleReview}
          disabled={loading}
        />

        <footer className="chat-footer">
          <ChatInput
            onSend={handleSend}
            disabled={loading || Boolean(review)}
          />

          {threadId && (
            <p className="thread-id">
              Conversation : {threadId.slice(0, 8)}
            </p>
          )}
        </footer>
      </section>
    </main>
  );
}

export default App;
