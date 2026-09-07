import 'dart:io';
import 'dart:typed_data';

import 'package:crypto/crypto.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_image_compress/flutter_image_compress.dart';
import 'package:google_mlkit_text_recognition/google_mlkit_text_recognition.dart';
import 'package:path_provider/path_provider.dart';
import 'package:image_picker/image_picker.dart';
import 'package:mime/mime.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import '../../config.dart';
import '../../data/hq.dart';

enum CaptureSource { camera, gallery, file }

class CaptureResult {
  CaptureResult({required this.receiptId, this.extractionError, this.duplicates = const [], this.isReceipt = true});
  final String receiptId;
  final String? extractionError;
  final List<Map<String, dynamic>> duplicates;
  final bool isReceipt;
}

/// Picks a receipt (camera / photo / file), shrinks it, uploads it to the vault,
/// creates the receipt row and asks the extract-receipt function to read it.
class ReceiptCapture {
  ReceiptCapture._();
  static final instance = ReceiptCapture._();

  static bool get hasCamera => Platform.isAndroid || Platform.isIOS;

  /// On-device text recognition (Android; free, offline). Returns null elsewhere.
  Future<String?> recognizeText(Uint8List imageBytes) async {
    if (!Platform.isAndroid && !Platform.isIOS) return null;
    File? tmp;
    try {
      final dir = await getTemporaryDirectory();
      tmp = File('${dir.path}${Platform.pathSeparator}hq-ocr-${DateTime.now().microsecondsSinceEpoch}.jpg');
      await tmp.writeAsBytes(imageBytes, flush: true);
      final recognizer = TextRecognizer(script: TextRecognitionScript.latin);
      try {
        final result = await recognizer.processImage(InputImage.fromFilePath(tmp.path));
        // Rebuild lines top-to-bottom so the parser sees a receipt-shaped text.
        final lines = <({double y, double x, String t})>[];
        for (final b in result.blocks) {
          for (final l in b.lines) {
            lines.add((y: l.boundingBox.top, x: l.boundingBox.left, t: l.text));
          }
        }
        lines.sort((a, b) => a.y != b.y ? a.y.compareTo(b.y) : a.x.compareTo(b.x));
        // Merge lines that sit on the same row (left label + right amount).
        final out = <String>[];
        double? lastY;
        for (final l in lines) {
          if (lastY != null && (l.y - lastY).abs() < 14 && out.isNotEmpty) {
            out[out.length - 1] = '${out.last}  ${l.t}';
          } else {
            out.add(l.t);
          }
          lastY = l.y;
        }
        final text = out.join('\n').trim();
        return text.isEmpty ? null : text;
      } finally {
        await recognizer.close();
      }
    } catch (_) {
      return null;
    } finally {
      try { await tmp?.delete(); } catch (_) {}
    }
  }

  Future<({Uint8List bytes, String mime, String ext})?> pick(CaptureSource source) async {
    if (source == CaptureSource.file) {
      final f = await FilePicker.pickFile(
        type: FileType.custom,
        allowedExtensions: const ['pdf', 'jpg', 'jpeg', 'png', 'webp', 'heic'],
      );
      if (f == null) return null;
      final bytes = await f.readAsBytes();
      final mime = lookupMimeType(f.name, headerBytes: bytes.take(64).toList()) ?? 'application/octet-stream';
      if (mime == 'application/pdf') return (bytes: bytes, mime: mime, ext: 'pdf');
      return _asJpeg(bytes);
    }
    final x = await ImagePicker().pickImage(
      source: source == CaptureSource.camera ? ImageSource.camera : ImageSource.gallery,
      maxWidth: 2200,
      imageQuality: 90,
    );
    if (x == null) return null;
    return _asJpeg(await x.readAsBytes());
  }

  Future<({Uint8List bytes, String mime, String ext})> _asJpeg(Uint8List raw) async {
    if (Platform.isAndroid || Platform.isIOS) {
      try {
        final out = await FlutterImageCompress.compressWithList(raw, minWidth: 1800, minHeight: 1800, quality: 82, format: CompressFormat.jpeg);
        return (bytes: Uint8List.fromList(out), mime: 'image/jpeg', ext: 'jpg');
      } catch (_) {/* fall through, upload as-is */}
    }
    final mime = lookupMimeType('x', headerBytes: raw.take(64).toList()) ?? 'image/jpeg';
    final ext = mime == 'image/png' ? 'png' : mime == 'image/webp' ? 'webp' : 'jpg';
    return (bytes: raw, mime: mime, ext: ext);
  }

  /// Upload + create rows + extract. Returns the receipt id even if extraction fails,
  /// so the user can fill it in by hand.
  Future<CaptureResult> upload({
    required Uint8List bytes,
    required String mime,
    required String ext,
    required String source, // camera | upload | manual
  }) async {
    final hq = Hq.instance;
    final sha = sha256.convert(bytes).toString();
    final ocrText = mime == 'application/pdf' ? null : await recognizeText(bytes);
    final now = DateTime.now();
    final id = _uuid();
    final path = 'receipts/${now.year}/${now.month.toString().padLeft(2, '0')}/$id.$ext';

    await hq.client.storage.from(HqConfig.vaultBucket).uploadBinary(
      path, bytes, fileOptions: FileOptions(contentType: mime, upsert: false));

    final file = await hq.client.from('hq_files').insert({
      'bucket': HqConfig.vaultBucket,
      'storage_path': path,
      'mime': mime,
      'bytes': bytes.length,
      'sha256': sha,
      'ocr_text': ocrText,
      'uploaded_via': source == 'camera' ? 'camera' : 'upload',
    }).select('id').single();

    final receipt = await hq.client.from('hq_receipts').insert({
      'file_id': file['id'],
      'source': source,
      'status': 'needs_review',
    }).select('id').single();
    final receiptId = receipt['id'] as String;

    return extract(receiptId);
  }

  Future<CaptureResult> extract(String receiptId) async {
    try {
      final res = await Hq.instance.client.functions.invoke('extract-receipt', body: {'receipt_id': receiptId});
      final data = res.data is Map ? Map<String, dynamic>.from(res.data as Map) : <String, dynamic>{};
      if (res.status >= 400 || data['ok'] == false || data['error'] != null) {
        return CaptureResult(receiptId: receiptId, extractionError: data['error']?.toString() ?? 'Could not read the receipt (${res.status})');
      }
      return CaptureResult(
        receiptId: receiptId,
        isReceipt: data['is_receipt'] != false,
        duplicates: ((data['duplicates'] as List?) ?? []).map((d) => Map<String, dynamic>.from(d as Map)).toList(),
      );
    } on FunctionException catch (e) {
      final d = e.details;
      final msg = d is Map && d['error'] != null ? d['error'].toString() : (e.reasonPhrase ?? 'Extraction failed (${e.status})');
      return CaptureResult(receiptId: receiptId, extractionError: msg);
    } catch (e) {
      return CaptureResult(receiptId: receiptId, extractionError: 'Extraction failed: $e');
    }
  }

  static String _uuid() {
    final r = DateTime.now().microsecondsSinceEpoch.toRadixString(16);
    final b = List<int>.generate(16, (i) => (DateTime.now().microsecond * (i + 7) + i * 31) & 0xff);
    final h = sha256.convert([...b, ...r.codeUnits]).toString();
    return '${h.substring(0, 8)}-${h.substring(8, 12)}-4${h.substring(13, 16)}-a${h.substring(17, 20)}-${h.substring(20, 32)}';
  }
}

/// Bottom sheet offering the capture sources. Returns the picked source.
Future<CaptureSource?> showCaptureSheet(BuildContext context) {
  return showModalBottomSheet<CaptureSource>(
    context: context,
    showDragHandle: true,
    builder: (ctx) => SafeArea(
      child: Column(mainAxisSize: MainAxisSize.min, children: [
        if (ReceiptCapture.hasCamera)
          ListTile(leading: const Icon(Icons.photo_camera), title: const Text('Take a photo'),
              onTap: () => Navigator.pop(ctx, CaptureSource.camera)),
        ListTile(leading: const Icon(Icons.photo_library_outlined), title: const Text('Choose from photos'),
            onTap: () => Navigator.pop(ctx, CaptureSource.gallery)),
        ListTile(leading: const Icon(Icons.picture_as_pdf_outlined), title: const Text('Choose a PDF or file'),
            onTap: () => Navigator.pop(ctx, CaptureSource.file)),
        const SizedBox(height: 8),
      ]),
    ),
  );
}

/// Full capture flow with progress UI. Navigates to the review screen on success.
Future<void> runCaptureFlow(BuildContext context, void Function(String receiptId) openReview) async {
  final source = await showCaptureSheet(context);
  if (source == null) return;
  final picked = await ReceiptCapture.instance.pick(source);
  if (picked == null || !context.mounted) return;
  final messenger = ScaffoldMessenger.of(context);
  messenger.showSnackBar(const SnackBar(content: Text('Reading and uploading the receipt…'), duration: Duration(seconds: 30)));
  try {
    final result = await ReceiptCapture.instance.upload(
      bytes: picked.bytes, mime: picked.mime, ext: picked.ext,
      source: source == CaptureSource.camera ? 'camera' : 'upload',
    );
    messenger.hideCurrentSnackBar();
    if (result.extractionError != null) {
      messenger.showSnackBar(SnackBar(content: Text('Saved, but not read: ${result.extractionError}'), duration: const Duration(seconds: 8)));
    } else if (!result.isReceipt) {
      messenger.showSnackBar(const SnackBar(content: Text('Saved. This does not look like a receipt; check the fields.')));
    } else if (result.duplicates.isNotEmpty) {
      messenger.showSnackBar(SnackBar(content: Text('Possible duplicate of ${result.duplicates.length} existing receipt(s)'), duration: const Duration(seconds: 6)));
    }
    openReview(result.receiptId);
  } catch (e) {
    messenger.hideCurrentSnackBar();
    messenger.showSnackBar(SnackBar(content: Text('Upload failed: $e')));
  }
}
