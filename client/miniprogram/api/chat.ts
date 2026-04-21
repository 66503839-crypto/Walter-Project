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

export const chat = (messages: ChatMessage[]) =>
  request<ChatResp>({
    url: '/chat',
    method: 'POST',
    data: { messages },
    showLoading: true,
  });
