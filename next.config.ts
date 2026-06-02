import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    unoptimized: true,
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'don16obqbay2c.cloudfront.net',
      },
    ],
  },
};

export default nextConfig;
