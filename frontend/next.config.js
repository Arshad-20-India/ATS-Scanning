/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Produces a minimal .next/standalone server bundle for Docker,
  // while letting Vercel handle native serverless deployment.
  ...(process.env.VERCEL ? {} : { output: "standalone" }),
};

module.exports = nextConfig;
