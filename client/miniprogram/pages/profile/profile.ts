import { logout } from '../../api/auth';

Page({
  data: {
    user: null as App.UserInfo | null,
  },

  onShow() {
    const app = getApp<App.IAppOption>();
    this.setData({ user: app.globalData.userInfo });
  },

  async onLogout() {
    const r = await wx.showModal({ title: '确认退出？', content: '' });
    if (!r.confirm) return;
    logout();
    const app = getApp<App.IAppOption>();
    app.globalData.userInfo = null;
    this.setData({ user: null });
    wx.reLaunch({ url: '/pages/index/index' });
  },

  async onRelogin() {
    logout();
    const app = getApp<App.IAppOption>();
    await app.login();
    this.setData({ user: app.globalData.userInfo });
  },
});
