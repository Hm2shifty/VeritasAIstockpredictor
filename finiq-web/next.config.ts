import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* Suppress yahoo-finance2 schema validation notices in production logs */
  serverExternalPackages: ["yahoo-finance2"],
  
  /* Allow images from common financial data sources */
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "logo.clearbit.com" },
      { protocol: "https", hostname: "**.yahoo.com" },
    ],
  },

  /* Silence the technicalindicators pkg warning about critical deps */
  webpack: (config) => {
    config.resolve.fallback = { ...config.resolve.fallback, fs: false };
    return config;
  },
  turbopack: {},
};

export default nextConfig;
