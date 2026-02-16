
import React from 'react';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

export interface Chat {
  id: string;
  title: string;
  is_pinned: boolean;
  created_at: string;
  updated_at: string;
}

export interface Reward {
  item: string;
  condition: string;
  chance: number;
  stack: number;
}

export interface MonsterIntel {
  name: string;
  weakness: string[];
  resistances: string[];
  breakableParts: string[];
  rewards: Record<string, Reward[]>;
  image: string;
}

export interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
}
