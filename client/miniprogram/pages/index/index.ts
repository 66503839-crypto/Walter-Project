Page({
  data: {
    nickname: '游客',
    loggedIn: false,
    features: [
      { icon: '✅', title: '待办事项', desc: '记录你的每日任务', path: '/pages/todo/todo' },
      { icon: '🤖', title: 'AI 对话', desc: '智能问答 / 创作助手', path: '/pages/chat/chat' },
      { icon: '👤', title: '个人中心', desc: '查看账号信息', path: '/pages/profile/profile' },
    ],
  },
  onShow() {
    this.refresh();
    // 登录是异步的，首次进入时 globalData 可能还没填好，稍后重试一次
    setTimeout(() => this.refresh(), 500);
  },
  refresh() {
    const app = getApp<App.IAppOption>();
    const user = app.globalData.userInfo;
    if (user) {
      // mock 登录没有 nickname，兜底显示 openid 前 8 位
      const display = user.nickname || (user.openid ? '用户 ' + user.openid.slice(-6) : '游客');
      this.setData({ nickname: display, loggedIn: true });
    } else {
      this.setData({ nickname: '游客', loggedIn: false });
    }
  },
  goTo(e: WechatMiniprogram.TouchEvent) {
    const { path } = e.currentTarget.dataset;
    wx.switchTab({ url: path }).catch(() => wx.navigateTo({ url: path }));
  },
});
