/**
 * 全局配置。
 *
 * ⚠️ 开发阶段（HTTP，需在微信开发者工具「详情 -> 本地设置」勾选「不校验合法域名」）
 * ✅ 上线前：换成自己的 HTTPS 域名，并在小程序后台添加 request 合法域名。
 */
// 生产服务器（开发阶段直连）
export const API_BASE_URL = 'http://81.71.89.228/api/v1';
// 本地开发（uvicorn --reload 时用）
// export const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';
// 上线后（HTTPS）
// export const API_BASE_URL = 'https://api.minigamer.your-domain.com/api/v1';

export const STORAGE_KEYS = {
  TOKEN: 'mg_access_token',
  REFRESH: 'mg_refresh_token',
  USER: 'mg_user_info',
} as const;
