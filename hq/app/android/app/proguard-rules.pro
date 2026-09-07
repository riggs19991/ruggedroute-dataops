# ML Kit text recognition: only the Latin model is bundled; the plugin references the
# other scripts' option classes, which we deliberately do not ship.
-dontwarn com.google.mlkit.vision.text.chinese.**
-dontwarn com.google.mlkit.vision.text.devanagari.**
-dontwarn com.google.mlkit.vision.text.japanese.**
-dontwarn com.google.mlkit.vision.text.korean.**
