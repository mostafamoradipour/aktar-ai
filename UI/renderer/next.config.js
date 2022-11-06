module.exports = {
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.target = 'electron-renderer';
    }
    config.resolve.mainFields = ['main', 'browser']
    return config;
  },
  images: {
    domains: ['api.kachrobotics.com'],
  },
  experimental: {
    images: {
      unoptimized: true
    }
  }
};
