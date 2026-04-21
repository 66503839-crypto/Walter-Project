import { ensureLoggedIn } from './api/auth';

App<App.IAppOption>({
  globalData: {
    token: '',
    userInfo: null,
  },
  async onLaunch() {
    try {
      const user = await ensureLoggedIn();
      this.globalData.userInfo = user;
      console.log('[App] 登录成功:', user.nickname || user.openid);
    } catch (e) {
      console.error('[App] 登录失败:', e);
      wx.showToast({
        title: '后端未就绪，以游客模式运行',
        icon: 'none',
        duration: 2500,
      });
    }
  },
  async login() {
    const user = await ensureLoggedIn();
    this.globalData.userInfo = user;
  },
});
