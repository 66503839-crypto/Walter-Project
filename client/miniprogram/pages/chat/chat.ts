import { chat, ChatMessage, listProviders, ProviderInfo } from '../../api/chat';
import { updateMe } from '../../api/auth';
import { STORAGE_KEYS } from '../../config';

interface ChatItem extends ChatMessage {
  id: string;
}

Page({
  data: {
    messages: [] as ChatItem[],
    input: '',
    sending: false,
    scrollToId: '',
    providers: [] as ProviderInfo[],
    currentProvider: '' as string, // 当前选中的 provider id，空字符串 = 跟随服务端默认
  },

  async onLoad() {
    // 1. 从本地 user 信息读已有偏好
    const user = wx.getStorageSync(STORAGE_KEYS.USER) as App.UserInfo | '';
    const pref = user ? user.preferred_provider || '' : '';
    this.setData({ currentProvider: pref });

    // 2. 拉取可用 provider 列表
    try {
      const list = await listProviders();
      this.setData({ providers: list });
      // 如果用户没偏好，默认选中第一个作为 UI 高亮（但不保存到后端）
      if (!pref && list.length > 0) {
        this.setData({ currentProvider: list[0].id });
      }
    } catch (e) {
      console.error('[chat] 拉取 providers 失败:', e);
    }
  },

  onInput(e: WechatMiniprogram.Input) {
    this.setData({ input: e.detail.value });
  },

  async onSwitchProvider(e: WechatMiniprogram.TouchEvent) {
    const { id } = e.currentTarget.dataset;
    if (!id || id === this.data.currentProvider) return;

    const prev = this.data.currentProvider;
    this.setData({ currentProvider: id });

    try {
      const updated = await updateMe({ preferred_provider: id });
      wx.setStorageSync(STORAGE_KEYS.USER, updated);
      wx.showToast({ title: '已切换', icon: 'success', duration: 1200 });
    } catch (e) {
      // 失败回滚
      this.setData({ currentProvider: prev });
      console.error('[chat] 切换 provider 失败:', e);
    }
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
      const res = await chat(payload, this.data.currentProvider || undefined);

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
