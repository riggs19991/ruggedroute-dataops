import 'package:flutter_test/flutter_test.dart';
import 'package:hq_app/updater/updater.dart';

void main() {
  test('a higher build number is an update', () {
    expect(Updater.isNewer(2, 1), isTrue);
    expect(Updater.isNewer(1, 1), isFalse);
    expect(Updater.isNewer(0, 1), isFalse);
  });

  test('release rows parse', () {
    final r = ReleaseInfo.fromRow({
      'version': '0.1.0',
      'build_number': 7,
      'storage_path': 'builds/android/hq-0.1.0-7.apk',
      'sha256': 'abc',
      'bytes': 123,
    });
    expect(r.version, '0.1.0');
    expect(r.buildNumber, 7);
    expect(r.notes, isNull);
  });
}
