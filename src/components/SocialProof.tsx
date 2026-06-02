import React from "react";
import Link from "next/link";

export default function SocialProof() {
  return (
    <section className="calypso-block calypso-block--EW19-tile-1 text-center align-center py-16 lg:py-28 bg-[#f5f5f5] px-5">
      <div className="max-w-[800px] mx-auto">
        <h2 className="h1 hpc-animate hpc-animate--from-left hpc-animate--delay-1 hpc-animate--animated text-[32px] lg:text-[48px] font-bold leading-tight text-[#191919] mb-6">
          只需点几下鼠标即可创建您的在线店铺。
        </h2>
        <p className="hpc-animate hpc-animate--from-left hpc-animate--delay-2 desktop-visible calypso-block__text hpc-animate--animated text-lg lg:text-xl text-[#4b4b4b] mb-10">
          与 160 万个信赖 Ecwid E‑commerce 平台的小型企业一起在线销售。
        </p>{" "}
        <Link
          href="/register"
          className="btn btn--large btn--hpc-shadow cta-signup inline-block bg-black text-white px-10 py-5 rounded-xl text-xl font-bold hover:bg-gray-800 transition-all shadow-xl shadow-gray-200"
        >
          创建商店
        </Link>
      </div>
    </section>
  );
}
