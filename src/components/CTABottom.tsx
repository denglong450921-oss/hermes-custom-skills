import React from 'react';
import Link from 'next/link';

export interface CTABottomProps {
  heading?: string;
  cta?: { label: string; href: string };
}

/**
 * CTABottom component - Final call to action before footer
 * 
 * Design Pattern: Centered Large CTA
 */
export default function CTABottom({
  heading = "开始在线销售",
  cta = { label: "创建商店", href: "/register" }
}: CTABottomProps) {
  return (
    <section className="calypso-block h-[345px] flex flex-col items-center justify-center bg-white">
      <div className="max-w-[1200px] mx-auto px-5 text-center w-full">
        <h2 className="text-[40px] lg:text-[64px] font-extrabold text-[#191919] mb-12 tracking-tight">
          {heading}
        </h2>
        <Link 
          href={cta.href}
          className="btn btn--large btn--yellow inline-block bg-black text-white px-12 py-6 rounded-2xl text-2xl font-bold hover:bg-gray-800 hover:scale-105 active:scale-95 transition-all shadow-2xl shadow-gray-200"
        >
          {cta.label}
        </Link>
      </div>
    </section>
  );
}
