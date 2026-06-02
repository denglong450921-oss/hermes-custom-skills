import Header from "@/components/Header";
import Hero from "@/components/Hero";
import SocialProof from "@/components/SocialProof";
import Feature from "@/components/Feature";
import CardsAndAwards from "@/components/CardsAndAwards";
import CTABottom from "@/components/CTABottom";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <>
      <Header />
      <main>
        <div className="h-[52px]"></div>
        <Hero
          heading="开始销售 免费在线"
          subheading="没有技术或设计技能？没问题！轻松打造一个既美观又易用的在线商店——并享受零交易手续费。"
          cta={{ label: "创建商店", href: "/register" }}
          image={{
            src: "https://d35z3p2poghz10.cloudfront.net/website/wp-content/themes/ecwid/images/hpc/phone-1-zh.png",
            alt: "开始销售",
          }}
        />
        <div className="h-[9px] md:h-[245px] lg:h-[430px]"></div>
        <SocialProof />
        <div className="h-[9px] md:h-[245px] lg:h-[429px]"></div>
        <Feature
          heading="随时随地销售"
          description="设置一次 Ecwid 店铺即可轻松地在网站、社交媒体、Amazon 等购物平台进行同步和销售，也支持面对面销售方式。 您可以先尝试一项，或全都试一试。"
          cta={{ label: "了解详情", href: "/sell-anywhere" }}
          image={{
            src: "https://d35z3p2poghz10.cloudfront.net/website/wp-content/themes/ecwid/images/hpc/slider-1-1-zh.png",
            alt: "随时随地销售",
          }}
        />
        <div className="h-[9px] md:h-[245px] lg:h-[386px]"></div>
        <Feature
          heading="更快地成长"
          description="您是否需要像 Google 和 Facebook 广告这样简单易用的营销工具来让您的企业快速成长？您找到了。"
          cta={{ label: "了解详情", href: "/promote" }}
          image={{
            src: "https://d35z3p2poghz10.cloudfront.net/website/wp-content/themes/ecwid/images/hpc/slider-2-1-zh.png",
            alt: "更快地成长",
          }}
          reverse={true}
        />
        <div className="h-[9px] md:h-[245px] lg:h-[264px]"></div>
        <Feature
          heading="管理简单"
          description="通过一个包含集中式存货、订单管理和定价等功能的信息中心管理一切事务。2023 年实现速度最快的电子商务平台。"
          cta={{ label: "了解详情", href: "/manage" }}
          image={{
            src: "https://d35z3p2poghz10.cloudfront.net/website/wp-content/themes/ecwid/images/hpc/slider-3-1-zh.png",
            alt: "管理简单",
          }}
        />
        <div className="h-[9px] md:h-[245px] lg:h-[265px]"></div>
        <CardsAndAwards />
        <div className="h-[9px] md:h-[245px] lg:h-[463px]"></div>
        <CTABottom />
      </main>
      <Footer />
    </>
  );
}
