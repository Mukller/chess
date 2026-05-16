import { useEffect, useState } from "react";

export function useTelegram() {
  const [tg, setTg] = useState<TelegramWebApp | null>(null);

  useEffect(() => {
    const webapp = window.Telegram?.WebApp ?? null;
    if (!webapp) return;
    webapp.ready();
    webapp.expand();
    setTg(webapp);
  }, []);

  return tg;
}

export function applyTelegramTheme(tg: TelegramWebApp | null): void {
  if (!tg) return;
  const root = document.documentElement;
  const theme = tg.themeParams ?? {};
  const entries: Array<[string, string | undefined]> = [
    ["--tg-theme-bg-color", theme.bg_color],
    ["--tg-theme-text-color", theme.text_color],
    ["--tg-theme-hint-color", theme.hint_color],
    ["--tg-theme-button-color", theme.button_color],
    ["--tg-theme-button-text-color", theme.button_text_color],
    ["--tg-theme-secondary-bg-color", theme.secondary_bg_color],
  ];
  for (const [name, value] of entries) {
    if (value) root.style.setProperty(name, value);
  }
}
