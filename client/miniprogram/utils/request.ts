/**
 * 统一 HTTP 封装：自动带 Authorization，统一错误提示。
 */
import { API_BASE_URL, STORAGE_KEYS } from '../config';

interface RequestOptions {
  url: string;
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  data?: unknown;
  auth?: boolean; // 默认 true
  showLoading?: boolean;
}

interface ApiResp<T> {
  code: number;
  message: string;
  data: T;
}

export function request<T = unknown>(opts: RequestOptions): Promise<T> {
  const {
    url,
    method = 'GET',
    data,
    auth = true,
    showLoading = false,
  } = opts;

  return new Promise<T>((resolve, reject) => {
    const header: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (auth) {
      const token = wx.getStorageSync(STORAGE_KEYS.TOKEN);
      if (token) {
        header['Authorization'] = `Bearer ${token}`;
      }
    }

    if (showLoading) wx.showLoading({ title: '加载中...', mask: true });

    wx.request({
      url: API_BASE_URL + url,
      method,
      data: data as WechatMiniprogram.IAnyObject,
      header,
      success: (res) => {
        const body = res.data as ApiResp<T>;
        if (res.statusCode === 401) {
          wx.removeStorageSync(STORAGE_KEYS.TOKEN);
          wx.showToast({ title: '请重新登录', icon: 'none' });
          reject(new Error('unauthorized'));
          return;
        }
        if (body.code === 0) {
          resolve(body.data);
        } else {
          wx.showToast({ title: body.message || '请求失败', icon: 'none' });
          reject(new Error(body.message));
        }
      },
      fail: (err) => {
        wx.showToast({ title: '网络错误', icon: 'none' });
        reject(err);
      },
      complete: () => {
        if (showLoading) wx.hideLoading();
      },
    });
  });
}
