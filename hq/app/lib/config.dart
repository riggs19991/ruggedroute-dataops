/// Public configuration. The Supabase publishable key is designed to be shipped in
/// clients; every HQ table is protected by row-level security that only the
/// allow-listed founder login can pass.
class HqConfig {
  static const supabaseUrl = 'https://tzucpijgyjhpgwukjsau.supabase.co';
  static const supabasePublishableKey = 'sb_publishable_qgSQd92ZSLnHIgGToevHuA_x8PVlxNP';
  static const releasesBucket = 'hq-releases';
  static const vaultBucket = 'hq-vault';
  static const appName = 'RuggedRoute HQ';
}
