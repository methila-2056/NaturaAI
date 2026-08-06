import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface UserProfile {
  id: string;
  fullName: string;
  email: string;
  age: number;
  gender: string;
  height?: number;
  weight?: number;
  country?: string;
  diseases: string[];
  allergies: string[];
  medications: string[];
  lifestyle?: string;
  dietaryPreferences?: string;
}

interface UserState {
  user: UserProfile | null;
  token: string | null;
  setAuth: (user: UserProfile, token: string) => void;
  updateProfile: (patch: Partial<UserProfile>) => void;
  logout: () => void;
}

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      setAuth: (user, token) => set({ user, token }),
      updateProfile: (patch) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...patch } : state.user,
        })),
      logout: () => set({ user: null, token: null }),
    }),
    { name: "naturaai-store" },
  ),
);
