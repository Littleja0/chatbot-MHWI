const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function getChatResponse(message: string, history: any[] = []) {
  try {
    const response = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Backend Error:", error);
    return "The Scoutflies are confused... I couldn't reach the Research Center (Backend). Please ensure the backend is running.";
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
