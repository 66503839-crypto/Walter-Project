import { chat, ChatMessage } from '../../api/chat';

interface ChatItem extends ChatMessage {
  id: string;
}

Page({
  data: {
    messages: [] as ChatItem[],
    input: '',
    sending: false,
    scrollToId: '',
  },

  onInput(e: WechatMiniprogram.Input) {
    this.setData({ input: e.detail.value });
  },

  async onSend() {
    const text = this.data.input.trim();
    if (!text || this.data.sending) return;

    const userMsg: ChatItem = {
      id: `u_${Date.now()}`,
      role: 'user',
      content: text,
    };
    const nextMessages = [...this.data.messages, userMsg];
    this.setData({
      messages: nextMessages,
      input: '',
      sending: true,
      scrollToId: userMsg.id,
    });

    try {
      const payload: ChatMessage[] = nextMessages.map(({ role, content }) => ({ role, content }));
      const res = await chat(payload);

      const botMsg: ChatItem = {
        id: `a_${Date.now()}`,
        role: 'assistant',
        content: res.content,
      };
      this.setData({
        messages: [...nextMessages, botMsg],
        scrollToId: botMsg.id,
      });
    } finally {
      this.setData({ sending: false });
    }
  },

  onClear() {
    this.setData({ messages: [] });
  },
});
