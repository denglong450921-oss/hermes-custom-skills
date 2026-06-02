import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ecwid E-commerce - 在 5 分钟内免费添加在线商店",
  description:
    "没有技术或设计技能？没问题！轻松打造一个既美观又易用的在线商店——并享受零交易手续费。",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
