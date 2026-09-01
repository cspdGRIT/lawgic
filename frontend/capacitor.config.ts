import type { CapacitorConfig } from '@capacitor/cli';

// appId is the iOS bundle ID / Android package name — cheap to change now, painful
// to change after the first App Store / Play Store submission. Update before release
// if com.lawgic.app isn't the final identifier.
const config: CapacitorConfig = {
  appId: 'com.lawgic.app',
  appName: 'Lawgic',
  webDir: 'dist',
  // 'https' (not the default 'http') so the Android WebView's origin matches iOS's
  // capacitor://localhost closely enough that Secure-cookie / secure-context logic
  // (relevant once the refresh-token flow is adapted for mobile) behaves consistently
  // across both platforms.
  server: {
    androidScheme: 'https',
  },
};

export default config;
