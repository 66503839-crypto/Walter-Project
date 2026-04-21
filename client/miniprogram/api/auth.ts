/**
 * 认证相关 API 封装。
 */
import { STORAGE_KEYS } from '../config';
import { request } from '../utils/request';

export interface LoginResp {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: App.UserInfo;
}

export function wxLogin(code: string, nickname?: string, avatar?: string) {
  return request<LoginResp>({
    url: '/auth/wx-login',
    method: 'POST',
    data: { code, nickname, avatar },
    auth: false,
  });
}

export function getMe() {
  return request<App.UserInfo>({ url: '/users/me' });
}

export async function ensureLoggedIn(): Promise<App.UserInfo> {
  const stored = wx.getStorageSync(STORAGE_KEYS.USER);
  if (stored) return stored as App.UserInfo;

  const { code } = await wx.login();
  const res = await wxLogin(code);
  wx.setStorageSync(STORAGE_KEYS.TOKEN, res.access_token);
  wx.setStorageSync(STORAGE_KEYS.REFRESH, res.refresh_token);
  wx.setStorageSync(STORAGE_KEYS.USER, res.user);
  return res.user;
}

export function logout() {
  wx.removeStorageSync(STORAGE_KEYS.TOKEN);
  wx.removeStorageSync(STORAGE_KEYS.REFRESH);
  wx.removeStorageSync(STORAGE_KEYS.USER);
}
