/**
 * 全局配置。
 *
 * 当前使用：腾讯内网 DevCloud CVM（HTTPS 由 AIO-Forward 网关处理）
 * 外层 Nginx 已把 /mg-api/ 反代到容器 :8000/api/，所以客户端这里就写 /mg-api
 * 切环境时改下方的 API_BASE_URL 常量即可
 */
// ✅ 线上：腾讯内网（iOA VPN 连上后可达）
export const API_BASE_URL = 'https://walteryang-any3.devcloud.woa.com/mg-api';
// 公网环境（之前的）
// export const API_BASE_URL = 'https://www.gamerw.online/api/v1';
// 本地开发（uvicorn --reload 跑在 127.0.0.1:8000）
// export const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

export const STORAGE_KEYS = {
  TOKEN: 'mg_access_token',
  REFRESH: 'mg_refresh_token',
  USER: 'mg_user_info',
} as const;
