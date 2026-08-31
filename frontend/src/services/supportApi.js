const API_URL =
  import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

async function readResponse(response) {
  const data = await response.json();

  if (!response.ok) {
    const message =
      data.detail ?? "Une erreur est survenue avec l'API.";
    throw new Error(message);
  }

  return data;
}

export async function sendMessage(message, threadId) {
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      thread_id: threadId,
    }),
  });

  return readResponse(response);
}

export async function reviewAction(threadId, decision) {
  const response = await fetch(
    `${API_URL}/chat/${threadId}/review`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ decision }),
    },
  );

  return readResponse(response);
}
