import 'dart:io';

import 'package:crypto/crypto.dart';
import 'package:http/http.dart' as http;
import 'package:open_filex/open_filex.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:path_provider/path_provider.dart';

import '../config.dart';
import '../data/hq.dart';

class ReleaseInfo {
  ReleaseInfo({
    required this.version,
    required this.buildNumber,
    required this.storagePath,
    this.sha256,
    this.notes,
    this.bytes,
  });
  final String version;
  final int buildNumber;
  final String storagePath;
  final String? sha256;
  final String? notes;
  final int? bytes;

  factory ReleaseInfo.fromRow(Map<String, dynamic> r) => ReleaseInfo(
        version: r['version'] as String,
        buildNumber: (r['build_number'] as num).toInt(),
        storagePath: r['storage_path'] as String,
        sha256: r['sha256'] as String?,
        notes: r['notes'] as String?,
        bytes: (r['bytes'] as num?)?.toInt(),
      );
}

/// Self-update without any app store: CI publishes builds into the private
/// `hq-releases` bucket and a row in `hq_app_releases`; the app compares build
/// numbers, downloads through a short-lived signed URL, verifies the SHA-256,
/// and hands the installer to the OS.
class Updater {
  Updater._();
  static final Updater instance = Updater._();

  static String? get platform =>
      Platform.isAndroid ? 'android' : Platform.isWindows ? 'windows' : null;

  /// True when [candidate] is newer than [current].
  static bool isNewer(int candidate, int current) => candidate > current;

  Future<ReleaseInfo?> checkForUpdate() async {
    final p = platform;
    if (p == null) return null;
    final info = await PackageInfo.fromPlatform();
    final current = int.tryParse(info.buildNumber) ?? 0;
    final rows = await Hq.instance.client
        .from('hq_app_releases')
        .select()
        .eq('platform', p)
        .order('build_number', ascending: false)
        .limit(1);
    if ((rows as List).isEmpty) return null;
    final rel = ReleaseInfo.fromRow(Map<String, dynamic>.from(rows.first));
    return isNewer(rel.buildNumber, current) ? rel : null;
  }

  /// Downloads and launches the installer. Reports progress 0..1.
  Future<void> downloadAndInstall(ReleaseInfo rel, void Function(double) onProgress) async {
    final url = await Hq.instance.client.storage
        .from(HqConfig.releasesBucket)
        .createSignedUrl(rel.storagePath, 600);
    final dir = await getTemporaryDirectory();
    final ext = Platform.isAndroid ? 'apk' : 'exe';
    final file = File('${dir.path}${Platform.pathSeparator}hq-update-${rel.buildNumber}.$ext');

    final client = http.Client();
    try {
      final resp = await client.send(http.Request('GET', Uri.parse(url)));
      if (resp.statusCode != 200) {
        throw Exception('Download failed (${resp.statusCode})');
      }
      final total = resp.contentLength ?? rel.bytes ?? 0;
      var received = 0;
      final sink = file.openWrite();
      final digestSink = _DigestSink();
      final hasher = sha256.startChunkedConversion(digestSink);
      await for (final chunk in resp.stream) {
        sink.add(chunk);
        hasher.add(chunk);
        received += chunk.length;
        if (total > 0) onProgress(received / total);
      }
      await sink.close();
      hasher.close();
      final digest = digestSink.value.toString();
      if (rel.sha256 != null && rel.sha256!.toLowerCase() != digest) {
        await file.delete();
        throw Exception('Downloaded file failed its integrity check. Not installing.');
      }
    } finally {
      client.close();
    }

    if (Platform.isAndroid) {
      final r = await OpenFilex.open(file.path, type: 'application/vnd.android.package-archive');
      if (r.type != ResultType.done) {
        throw Exception('Could not open the installer: ${r.message}');
      }
    } else if (Platform.isWindows) {
      await Process.start(file.path, const [], mode: ProcessStartMode.detached);
      exit(0);
    }
  }
}

class _DigestSink implements Sink<Digest> {
  late Digest value;
  @override
  void add(Digest data) => value = data;
  @override
  void close() {}
}
