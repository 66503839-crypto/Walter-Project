/// <reference path="../node_modules/miniprogram-api-typings/index.d.ts" />

// 自定义全局类型
declare namespace App {
  interface IAppOption {
    globalData: {
      token: string;
      userInfo: UserInfo | null;
    };
    login: () => Promise<void>;
  }

  interface UserInfo {
    id: number;
    openid: string;
    nickname?: string;
    avatar?: string;
  }
}
