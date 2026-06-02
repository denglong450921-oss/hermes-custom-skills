import React from "react";
import Image from "next/image";
import Link from "next/link";

export interface HeroProps {
  heading?: string;
  subheading?: string;
  cta?: { label: string; href: string };
  image?: { src: string; alt: string };
}

/**
 * Hero component - Top section with title and illustration
 *
 * Design Pattern: Centered Hero with Illustration
 */
export default function Hero({
  heading = "开始销售 Instagram",
  subheading = "没有技术或设计技能？没问题！轻松打造一个既美观又易用的在线商店——并享受零交易手续费。",
  cta = { label: "创建商店", href: "/register" },
  image = {
    src: "https://don16obqbay2c.cloudfront.net/wp-content/themes/ecwid/images/hpc/zh-CN/png_illustrations/Website_mob.png",
    alt: "Ecwid Illustration",
  },
}: HeroProps) {
  return (
    <section className="calypso-block calypso-block--EW19-tile-1 pt-32 pb-20 lg:pt-[200px] lg:pb-[200px] bg-white overflow-hidden">
      <div className="hidden">
        var imgPath = CDN + &quot;/wp-content/themes/ecwid/images/hpc/&quot;; function get_lang_prefix() &#123; return &apos;zh-CN&apos;; &#125; function get_
      </div>
      <div className="max-w-[1200px] mx-auto px-5 flex flex-col lg:flex-row items-center justify-between">
        {/* Content */}
        <div className="w-full lg:w-1/2 max-w-[512px] text-left animate-in fade-in slide-in-from-bottom-10 duration-1000">
          <h1 className="h1--EW19 hpc-animate hpc-animate--from-left hpc-animate--delay-1 hpc-animate--animated text-[44px] lg:text-[64px] font-[800] leading-[1.1] tracking-tight text-[#191919] mb-8">
            开始销售 免费在线
          </h1>
          <p className="hpc-animate hpc-animate--from-left hpc-animate--delay-2 calypso-block__text hpc-animate--animated text-xl lg:text-2xl text-[#4b4b4b] leading-relaxed mb-10">
            {subheading}
          </p>
          {" "}
          <Link
            href={cta.href}
            className="btn btn--large btn--hpc-shadow cta-signup inline-block bg-black text-white px-10 py-5 rounded-xl text-xl font-bold hover:bg-gray-800 hover:scale-105 active:scale-95 transition-all shadow-xl shadow-gray-200"
          >
            {cta.label}
          </Link>
        </div>

        {/* Visual */}
        <div className="w-full lg:w-1/2 mt-16 lg:mt-0 relative h-[300px] lg:h-[600px] animate-in fade-in zoom-in-95 duration-1000 delay-300">
          <img
            src={image.src}
            alt={image.alt}
            className="hpc-phone__image object-contain w-full h-full"
          />
          <img src={image.src} alt="" className="hpc-phone__image hidden" />
          <img src={image.src} alt="" className="hpc-tablet__image hidden" />
          <img src={image.src} alt="" className="hpc-tablet__image hidden" />
        </div>
      </div>
    </section>
  );
}
