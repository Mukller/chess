export {};

declare global {
  interface TelegramThemeParams {
    bg_color?: string;
    text_color?: string;
    hint_color?: string;
    link_color?: string;
    button_color?: string;
    button_text_color?: string;
    secondary_bg_color?: string;
  }

  interface TelegramWebAppUser {
    id: number;
    first_name: string;
    last_name?: string;
    username?: string;
    language_code?: string;
    photo_url?: string;
    is_premium?: boolean;
  }

  interface TelegramWebApp {
    initData: string;
    initDataUnsafe: {
      user?: TelegramWebAppUser;
      auth_date?: number;
      hash?: string;
    };
    version: string;
    colorScheme: "light" | "dark";
    themeParams: TelegramThemeParams;
    isExpanded: boolean;
    viewportHeight: number;
    viewportStableHeight: number;
    HapticFeedback?: {
      impactOccurred: (style: "light" | "medium" | "heavy" | "rigid" | "soft") => void;
      notificationOccurred: (type: "error" | "success" | "warning") => void;
      selectionChanged: () => void;
    };
    ready: () => void;
    expand: () => void;
    close: () => void;
    MainButton: {
      text: string;
      isVisible: boolean;
      show: () => void;
      hide: () => void;
      setText: (text: string) => void;
      onClick: (cb: () => void) => void;
      offClick: (cb: () => void) => void;
    };
    BackButton: {
      isVisible: boolean;
      show: () => void;
      hide: () => void;
      onClick: (cb: () => void) => void;
      offClick: (cb: () => void) => void;
    };
    showAlert: (message: string) => void;
    sendData: (data: string) => void;
  }

  interface Window {
    Telegram?: {
      WebApp: TelegramWebApp;
    };
  }
}
