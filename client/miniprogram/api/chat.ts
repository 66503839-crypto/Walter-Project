/** AI 对话 API。 */
import { request } from '../utils/request';

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface ChatResp {
  content: string;
  model: string;
  provider: string;
}

export interface ProviderInfo {
  id: string;
  name: string;
  desc: string;
}

export const chat = (messages: ChatMessage[], provider?: string) =>
  request<ChatResp>({
    url: '/chat',
    method: 'POST',
    data: { messages, provider },
    showLoading: true,
  });

export const listProviders = () =>
  request<ProviderInfo[]>({
    url: '/chat/providers',
    method: 'GET',
  });
