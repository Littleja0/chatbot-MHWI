const API_URL = import.meta.env.VITE_API_URL || '';

export async function getChatResponse(message: string, history: any[] = []) {
  // Timeout de 90s para evitar loading infinito
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 90000);

  try {
    const response = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      const detail = errorData?.detail || 'Network response was not ok';
      throw new Error(detail);
    }

    const data = await response.json();
    return data;
  } catch (error: any) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      console.error("Request timed out after 90s");
      return "⏰ A requisição demorou demais e foi cancelada. Tente novamente com uma pergunta mais simples.";
    }
    console.error("Backend Error:", error);
    return error.message || "The Scoutflies are confused... I couldn't reach the Research Center (Backend). Please ensure the backend is running.";
  }
}

export async function getMonsterIntel(monsterName: string) {
  try {
    const response = await fetch(`${API_URL}/monster/${monsterName}`);

    if (!response.ok) {
      if (response.status === 404) {
        console.warn(`Monster ${monsterName} not found.`);
        return null;
      }
      throw new Error('Network response was not ok');
    }

    const data = await response.json();
    return {
      weakness: data.weakness || [],
      resistances: data.resistances || [],
      breakableParts: data.breakableParts || [],
      rewards: data.rewards || {},
      image: data.image
    };
  } catch (error) {
    console.error("Intel Error:", error);
    return null;
  }
}
