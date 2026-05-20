import { useCallback, useState } from "react";

export interface CardMatch {
  card_id: number;
  title: string;
  description: string;
  similarity: number;
}

export interface CardSearchState {
  results: CardMatch[];
  isLoading: boolean;
  error: string | null;
}

export function useCardSearch() {
  const [state, setState] = useState<CardSearchState>({
    results: [],
    isLoading: false,
    error: null,
  });

  const searchCards = useCallback(async (imageDataUrl: string, classId?: number) => {
    setState({ results: [], isLoading: true, error: null });

    try {
      const body: Record<string, unknown> = { image_data: imageDataUrl, top_k: 5 };
      if (classId !== undefined) body.class_id = classId;
      const response = await fetch("/api/card-search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.error || `Ошибка ${response.status}`);
      }

      const data = await response.json();
      setState({
        results: data.results || [],
        isLoading: false,
        error: null,
      });
    } catch (err) {
      setState({
        results: [],
        isLoading: false,
        error: (err as Error).message || "Ошибка поиска карточек",
      });
    }
  }, []);

  const clearResults = useCallback(() => {
    setState({ results: [], isLoading: false, error: null });
  }, []);

  return { ...state, searchCards, clearResults };
}
