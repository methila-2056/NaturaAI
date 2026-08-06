/** @type {import("next").NextConfig} */
const nextConfig = {
  output: "standalone",
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "naturaai-assets.s3.amazonaws.com" },
    ],
  },
};

export default nextConfig;
