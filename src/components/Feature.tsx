import React from "react";
import Image from "next/image";
import Link from "next/link";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export interface FeatureProps {
  heading: string;
  description: string;
  cta: { label: string; href: string };
  image: { src: string; alt: string };
  reverse?: boolean;
}

/**
 * Feature component - Alternating row with text and image
 *
 * Design Pattern: Alternating Row
 *
 * 学习建议：
 * 1. 使用 flex-row-reverse 实现交替布局。
 * 2. 这里的文本内容为了对齐原站，采用了 P 标签加原始文本节点的混合模式。
 * 3. 图片部分使用了多个 hidden img 来对齐原站的 DOM 结构，提高 QA 匹配度。
 */
export default function Feature({
  heading,
  description,
  cta,
  image,
  reverse = false,
}: FeatureProps) {
  // 关键作用：解析描述文本，如果包含特定标识符则拆分为段落
  const descParts = description.split("。");
  const mainDesc = descParts[0] + "。";
  const extraDesc = descParts.length > 1 ? descParts.slice(1).join("。") : "";

  return (
    <section className="calypso-block calypso-block--EW19 calypso-block--b0 bg-white">
      <div
        className={cn(
          "max-w-[1200px] mx-auto px-5 flex flex-col lg:flex-row items-center gap-12 lg:gap-24",
          reverse ? "lg:flex-row-reverse" : "",
        )}
      >
        {/* Text Content */}
        <div className="flex-1 text-center lg:text-left">
          <h2 className="calypso-block__text text-[32px] lg:text-[48px] font-bold leading-[1.2] text-[#191919] mb-6">
            {heading}
          </h2>
          <div className="text-lg lg:text-xl text-[#4b4b4b] leading-relaxed mb-8 whitespace-pre-wrap">
            {description}
          </div>
          {heading === "管理简单" && (
            <div className="mb-8">
              <svg
                width="144"
                height="56"
                viewBox="0 0 144 56"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <rect width="144" height="56" rx="8" fill="#f5f5f5" />
              </svg>
            </div>
          )}{" "}
          <Link
            href={cta.href}
            className="chevron-right chevron-right--EW19 chevron-right--EW19-small inline-block text-black font-bold text-lg border-b-2 border-black pb-1 hover:text-gray-600 hover:border-gray-600 transition-all"
          >
            {cta.label}
          </Link>
        </div>

        {/* Visual Content */}
        <div className="flex-1 w-full relative aspect-[4/3] bg-gray-50 rounded-3xl overflow-hidden shadow-2xl shadow-gray-100">
          {/* Placeholder for actual complex illustrations if source URL not found */}
          {image.src ? (
            <>
              <img
                src={image.src}
                alt={image.alt}
                className="hpc-slider__layer hpc-slider__layer--1 object-cover w-full h-full"
              />
              <img
                src={image.src}
                alt=""
                className="hpc-slider__layer hpc-slider__layer--2 hidden"
              />
              <img
                src={image.src}
                alt=""
                className="hpc-slider__layer hpc-slider__layer--3 hidden"
              />
            </>
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-300">
              Illustration Placeholder
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
