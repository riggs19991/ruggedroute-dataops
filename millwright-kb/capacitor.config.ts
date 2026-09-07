import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.millwrightkb.app',
  appName: 'Millwright KB',
  webDir: 'dist',
  // The web app is served from the native shell; Supabase is reached over HTTPS as usual.
  server: { androidScheme: 'https' },
  ios: { contentInset: 'automatic' },
};

export default config;
