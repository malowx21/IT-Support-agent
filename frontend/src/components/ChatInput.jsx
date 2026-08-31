import { useState } from "react";

function ChatInput({ onSend, disabled }) {
  const [question, setQuestion] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();

    const cleanedQuestion = question.trim();

    if (!cleanedQuestion || disabled) {
      return;
    }

    await onSend(cleanedQuestion);
    setQuestion("");
  }

  return (
    <form className="question-form" onSubmit={handleSubmit}>
      <label htmlFor="question">Votre question</label>

      <div className="input-group">
        <input
          id="question"
          type="text"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Décrivez votre problème..."
          disabled={disabled}
          autoComplete="off"
        />

        <button
          type="submit"
          disabled={disabled || !question.trim()}
        >
          {disabled ? "En cours..." : "Envoyer"}
        </button>
      </div>
    </form>
  );
}

export default ChatInput;
