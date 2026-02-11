
// Fix: Added React import to resolve namespace error for React.ReactNode
import React from 'react';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
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
