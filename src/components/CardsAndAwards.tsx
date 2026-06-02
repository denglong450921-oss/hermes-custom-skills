import React from "react";
import Link from "next/link";

export default function CardsAndAwards() {
  return (
    <section className="bg-white">
      <div className="max-w-[1440px] mx-auto px-[112px]">
        <div className="flex flex-col md:flex-row gap-[351px]">
          <Link
            href="/support"
            className="rounded-2xl hover:-translate-y-2 transition-transform duration-300 flex flex-col items-center text-center"
          >
            <div className="w-[97px] h-[94px] mb-6 flex items-center justify-center text-[#016dd2]">
              {/* Hands together icon */}
              <svg
                width="97"
                height="94"
                viewBox="0 0 97 94"
                fill="currentColor"
              >
                <title>Hands together</title>
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
              </svg>
            </div>
            <h3 className="hidden">Hands together</h3>
          </Link>

          <Link
            href="/apps"
            className="rounded-2xl hover:-translate-y-2 transition-transform duration-300 flex flex-col items-center text-center"
          >
            <div className="w-[95px] h-[94px] mb-6 flex items-center justify-center text-[#016dd2]">
              {/* App store icon */}
              <svg
                width="95"
                height="94"
                viewBox="0 0 95 94"
                fill="currentColor"
              >
                <title>Ecwid app store</title>
                <path d="M16 6l2.29 2.29L12.59 14l-4.29-4.3L6 12l6.59 6.59L24.18 7.01 22.17 5 12 15.17 7.41 10.59 6 12l6 6 13.59-13.59L24.18 3 12 15.17 7.41 10.59 6 12l6 6 13.59-13.59L24.18 3z" />
              </svg>
            </div>
            <h3 className="hidden">Ecwid app store</h3>
          </Link>

          <Link
            href="/mobile"
            className="rounded-2xl hover:-translate-y-2 transition-transform duration-300 flex flex-col items-center text-center"
          >
            <div className="w-[84px] h-[94px] mb-6 flex items-center justify-center text-[#016dd2]">
              {/* Mobile icon */}
              <svg
                width="84"
                height="94"
                viewBox="0 0 84 94"
                fill="currentColor"
              >
                <title>Mobile apps</title>
                <path d="M17 1.01L7 1c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 19H7V5h10v14z" />
              </svg>
            </div>
            <h3 className="hidden">Mobile apps</h3>
          </Link>
        </div>

        <div className="flex flex-wrap justify-center items-center gap-10 opacity-60 grayscale">
          {/* Awards images placeholders - in a real clone we should use the actual images */}
          <div className="w-24 h-24 bg-gray-200 rounded-full"></div>
          <div className="w-24 h-24 bg-gray-200 rounded-full"></div>
          <div className="w-24 h-24 bg-gray-200 rounded-full"></div>
          <div className="w-24 h-24 bg-gray-200 rounded-full"></div>
          <div className="w-24 h-24 bg-gray-200 rounded-full"></div>
        </div>
      </div>
    </section>
  );
}
