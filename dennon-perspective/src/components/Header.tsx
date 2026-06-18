"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Menu, X } from "lucide-react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Utility to merge tailwind classes
 */
function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export interface HeaderProps {
  navLinks?: Array<{ label: string; href: string }>;
  cta?: { label: string; href: string };
}

/**
 * Header component - Sticky navigation with mobile menu
 *
 * Design Pattern: Sticky-scroll header
 */
export default function Header({
  navLinks = [
    { label: "销售", href: "/sell" },
    { label: "推广", href: "/promote" },
    { label: "管理", href: "/manage" },
  ],
  cta = { label: "开始", href: "/register" },
}: HeaderProps) {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <header
      className={cn(
        "fixed top-0 left-0 right-0 z-50 transition-all duration-300 pt-[21px] pb-[17px]",
        isScrolled
          ? "bg-white/80 backdrop-blur-md shadow-sm"
          : "bg-transparent",
      )}
    >
      <div className="max-w-[1440px] mx-auto w-full px-[72px] flex justify-between items-center">
        {/* Logo */}
        <Link href="/" className="flex items-center">
          <svg
            width="106"
            height="32"
            viewBox="0 0 106 32"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="text-[#016dd2]"
          >
            <path
              d="M10.6 0H0V32H10.6V0ZM21.2 0H31.8V32H21.2V0ZM42.4 0H53V32H42.4V0ZM63.6 0H74.2V32H63.6V0ZM84.8 0H95.4V32H84.8V0ZM106 0V32H95.4V0H106Z"
              fill="currentColor"
            />
          </svg>
        </Link>

        {/* Desktop Nav */}
        <nav className="hidden lg:flex items-center gap-10">
          {navLinks.map((link) => (
            <Link
              key={link.label}
              href={link.href}
              className="calypso-menu__link text-[#191919] font-medium hover:text-gray-600 transition-colors"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Actions */}
        <div className="hidden lg:flex items-center gap-6">
          <Link
            href="/login"
            className="calypso-menu__link text-[#191919] font-medium hover:text-gray-600"
          >
            登录
          </Link>
          <Link
            href={cta.href}
            className="btn btn--small btn--nowrap cta-signup bg-black text-white px-6 py-2.5 rounded-lg font-bold hover:bg-gray-800 transition-all active:scale-95"
          >
            {cta.label}
          </Link>
        </div>

        {/* Mobile Toggle */}
        <button
          className="lg:hidden p-2 text-black"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
        >
          {isMenuOpen ? <X size={28} /> : <Menu size={28} />}
        </button>
      </div>

      {/* Mobile Menu Drawer */}
      <div
        className={cn(
          "fixed inset-0 top-20 bg-white z-40 lg:hidden transition-transform duration-300 ease-in-out",
          isMenuOpen ? "translate-x-0" : "translate-x-full",
        )}
      >
        <div className="flex flex-col p-8 gap-6 text-xl font-bold">
          {navLinks.map((link) => (
            <Link
              key={link.label}
              href={link.href}
              onClick={() => setIsMenuOpen(false)}
            >
              {link.label}
            </Link>
          ))}
          <div className="h-px bg-gray-100 my-4" />
          <Link href="/login" onClick={() => setIsMenuOpen(false)}>
            登录
          </Link>
          <Link
            href={cta.href}
            className="bg-black text-white px-6 py-4 rounded-xl text-center"
            onClick={() => setIsMenuOpen(false)}
          >
            {cta.label}
          </Link>
        </div>
      </div>
    </header>
  );
}
