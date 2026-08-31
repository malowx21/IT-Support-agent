function ReviewPanel({ review, onDecision, disabled }) {
  if (!review) {
    return null;
  }

  const toolCalls = review.tool_calls ?? [];

  return (
    <aside className="review-panel">
      <div>
        <span className="review-label">Validation humaine</span>
        <h2>{review.question}</h2>
      </div>

      {toolCalls.map((toolCall) => (
        <div className="tool-call" key={toolCall.id}>
          <strong>{toolCall.name}</strong>
          <pre>{JSON.stringify(toolCall.args, null, 2)}</pre>
        </div>
      ))}

      <div className="review-actions">
        <button
          className="button-reject"
          type="button"
          disabled={disabled}
          onClick={() => onDecision("reject")}
        >
          Rejeter
        </button>

        <button
          className="button-approve"
          type="button"
          disabled={disabled}
          onClick={() => onDecision("approve")}
        >
          Approuver
        </button>
      </div>
    </aside>
  );
}

export default ReviewPanel;
