/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Produces a minimal .next/standalone server bundle -- only the
  // node_modules actually needed at runtime get traced in, so the
  // Docker runtime image doesn't need the full node_modules tree.
  output: "standalone",
};

module.exports = nextConfig;
