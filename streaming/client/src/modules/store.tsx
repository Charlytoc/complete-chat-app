import { createWithEqualityFn as create } from "zustand/traditional";

import { TConversationData } from "../types/chatTypes";
import { getConversation, initConversation } from "./apiCalls";
import { TAttachment } from "../types";

type Message = {
  sender: string;
  text: string;
  imageUrl?: string;
};

type Model = {
  name: string;
  provider: string;
};

type Store = {
  credits: number;
  useCredit: (amount: number) => void;
};

export const useStore = create<Store>()((set) => ({
  credits: 4,
  useCredit: (amount) => set((state) => ({ credits: state.credits - amount })),
}));
