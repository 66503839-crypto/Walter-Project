Page({
  data: {
    nickname: '游客',
    features: [
      { icon: '✅', title: '待办事项', desc: '记录你的每日任务', path: '/pages/todo/todo' },
      { icon: '🤖', title: 'AI 对话', desc: '智能问答 / 创作助手', path: '/pages/chat/chat' },
      { icon: '👤', title: '个人中心', desc: '查看账号信息', path: '/pages/profile/profile' },
    ],
  },
  onShow() {
    const app = getApp<App.IAppOption>();
    const user = app.globalData.userInfo;
    this.setData({ nickname: user?.nickname || '游客' });
  },
  goTo(e: WechatMiniprogram.TouchEvent) {
    const { path } = e.currentTarget.dataset;
    wx.switchTab({ url: path }).catch(() => wx.navigateTo({ url: path }));
  },
});
