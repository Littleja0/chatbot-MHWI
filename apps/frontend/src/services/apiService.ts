
const API_URL = import.meta.env.VITE_API_URL || '';

export async function getChatResponse(message: string, chatId: string | null = null) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 90000);

  try {
    const response = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message, chat_id: chatId }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let detail = 'Network response was not ok';
      try {
        const errorData = await response.json();
        detail = errorData?.detail || detail;
      } catch (e) {
        detail = `${response.status} ${response.statusText}`;
      }
      throw new Error(detail);
    }

    const data = await response.json();
    return data;
  } catch (error: any) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      return "⏰ A requisição demorou demais e foi cancelada. Tente novamente com uma pergunta mais simples.";
    }
    return error.message || "Error connecting to backend.";
  }
}

export async function getChats() {
  const res = await fetch(`${API_URL}/chats`);
  return res.json();
}

export async function createChat(title?: string) {
  const res = await fetch(`${API_URL}/chats`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title })
  });
  return res.json();
}

export async function getHistory(chatId: string) {
  const res = await fetch(`${API_URL}/chats/${chatId}/history`);
  return res.json();
}

export async function deleteChat(chatId: string) {
  await fetch(`${API_URL}/chats/${chatId}`, { method: 'DELETE' });
}

export async function pinChat(chatId: string) {
  await fetch(`${API_URL}/chats/${chatId}/pin`, { method: 'PATCH' });
}

export async function renameChat(chatId: string, title: string) {
  await fetch(`${API_URL}/chats/${chatId}/title`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title })
  });
}

export async function getMonsterIntel(monsterName: string) {
  try {
    const response = await fetch(`${API_URL}/monster/${monsterName}`);
    if (!response.ok) return null;
    return response.json();
  } catch (error) {
    return null;
  }
}
