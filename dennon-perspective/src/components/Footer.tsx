import React from "react";
import Link from "next/link";
import { Facebook, Instagram, Twitter, Youtube } from "lucide-react";

export interface FooterProps {
  copyright?: string;
}

/**
 * Footer component - Site map and legal info
 *
 * Design Pattern: Multi-column links
 */
export default function Footer({
  copyright = "© 2026 Ecwid by Lightspeed",
}: FooterProps) {
  const footerSections = [
    {
      title: "在线销售",
      links: [
        { label: "到处销售", href: "/sell" },
        { label: "在 Facebook 上销售", href: "/facebook" },
        { label: "在 Instagram 上销售", href: "/instagram" },
        { label: "在 Amazon 上销售", href: "/amazon" },
      ],
    },
    {
      title: "推广",
      links: [
        { label: "Google 广告", href: "/google-ads" },
        { label: "Facebook 广告", href: "/facebook-ads" },
        { label: "电子邮件营销", href: "/email-marketing" },
      ],
    },
    {
      title: "管理",
      links: [
        { label: "支付方式", href: "/payments" },
        { label: "运送方式", href: "/shipping" },
        { label: "移动应用", href: "/mobile-app" },
      ],
    },
    {
      title: "支持",
      links: [
        { label: "帮助中心", href: "/support" },
        { label: "博客", href: "/blog" },
        { label: "播客", href: "/podcast" },
      ],
    },
  ];

  return (
    <footer className="bg-[#f5f5f5] h-[583px] py-16 text-[#191919] overflow-hidden">
      <div className="max-w-[1440px] mx-auto px-[72px]">
        <div className="mb-12">
          <svg
            width="114"
            height="34"
            viewBox="0 0 114 34"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="text-[#016dd2]"
          >
            <path
              d="M11.4 0H0V34H11.4V0ZM22.8 0H34.2V34H22.8V0ZM45.6 0H57V34H45.6V0ZM68.4 0H79.8V34H68.4V0ZM91.2 0H102.6V34H91.2V0ZM114 0V34H102.6V0H114Z"
              fill="currentColor"
            />
          </svg>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-8">
          {footerSections.map((section) => (
            <div key={section.title}>
              <h3 className="font-bold text-lg mb-6 uppercase tracking-wider">
                {section.title}
              </h3>
              <ul className="flex flex-col gap-4">
                {section.links.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="text-gray-600 hover:text-black transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Region Links */}
        <div className="pt-8 border-t border-gray-200 mb-8">
          <ul className="flex flex-wrap gap-4 text-sm text-gray-500">
            {[
              "China",
              "Argentina",
              "Denmark",
              "Italy",
              "Peru",
              "Sweden",
              "Brazil",
              "Egypt",
              "Japan",
              "Philippines",
              "Thailand",
              "Bulgaria",
              "Finland",
              "Korea",
              "Poland",
              "Türkiye",
              "Canada (English)",
              "France",
              "Latvia",
              "Portugal",
              "USA",
              "Canada (Français)",
              "Germany",
              "Lithuania",
              "Romania",
              "Venezuela",
              "Greece",
              "Mexico",
              "Slovakia",
              "Vietnam",
              "Colombia",
              "Hungary",
              "Netherlands",
              "Slovenia",
              "United Arab Emirates",
              "Croatia",
              "Indonesia",
              "Norway",
              "Spain",
              "Global",
              "Czech Republic",
            ].map((country) => (
              <li key={country}>
                <Link href="#" className="hover:text-black">
                  {country}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        {/* Bottom Bar */}
        <div className="mt-16 pt-8 border-t border-gray-200 flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex gap-4">
            <a href="#" className="icon-blog text-gray-500 hover:text-black">
              <span className="sr-only">(opens in new window)</span>
            </a>
            <a href="#" className="icon-podcast text-gray-500 hover:text-black">
              <span className="sr-only">(opens in new window)</span>
            </a>
            <a
              href="#"
              className="icon-pinterest text-gray-500 hover:text-black"
            >
              (opens in new window)
            </a>
            <a
              href="#"
              className="icon-facebook text-gray-500 hover:text-black"
            >
              (opens in new window)
            </a>
            <a href="#" className="icon-twitter text-gray-500 hover:text-black">
              (opens in new window)
            </a>
            <a
              href="#"
              className="icon-instagram text-gray-500 hover:text-black"
            >
              (opens in new window)
            </a>
            <a href="#" className="icon-youtube text-gray-500 hover:text-black">
              (opens in new window)
            </a>
          </div>
          <div className="text-sm text-gray-500">
            &copy; {new Date().getFullYear()} Ecwid.
          </div>
        </div>
      </div>
    </footer>
  );
}
