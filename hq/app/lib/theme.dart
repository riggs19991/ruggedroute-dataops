import 'package:flutter/material.dart';

/// Addictive Media Productions brand: neon green on black, charcoal surfaces,
/// off-white text, a condensed italic display face that echoes the wordmark.
/// Colors sampled from the logo files (AMP_LOGO_BACKGROUND.png etc.).
class AmpBrand {
  AmpBrand._();
  static const green = Color(0xFF38F800);      // signature neon green
  static const greenDim = Color(0xFF1FA300);   // pressed / containers
  static const greenGlow = Color(0x5938F800);  // 35% for borders and glows
  static const black = Color(0xFF000000);
  static const ink = Color(0xFF0A0A0A);        // page background
  static const surface = Color(0xFF141414);    // cards
  static const surfaceHigh = Color(0xFF1C1C1C);
  static const charcoal = Color(0xFF282828);   // logo's secondary gray, borders
  static const textPrimary = Color(0xFFE8E8E8);
  static const textSecondary = Color(0xFF9A9A9A);
  static const amber = Color(0xFFFFAB40);      // due-soon
  static const red = Color(0xFFFF5252);        // overdue / error

  static const displayFamily = 'BarlowCondensed';

  static const wordmark = 'assets/brand/amp_wordmark.png';
  static const mark = 'assets/brand/amp_mark.png';
  static const topo = 'assets/brand/amp_topo.jpg';

  static ThemeData dark() {
    const scheme = ColorScheme(
      brightness: Brightness.dark,
      primary: green,
      onPrimary: black,
      primaryContainer: greenDim,
      onPrimaryContainer: textPrimary,
      secondary: amber,
      onSecondary: black,
      secondaryContainer: Color(0xFF5A3A00),
      onSecondaryContainer: textPrimary,
      tertiary: green,
      onTertiary: black,
      error: red,
      onError: black,
      errorContainer: Color(0xFF5A1414),
      onErrorContainer: textPrimary,
      surface: ink,
      onSurface: textPrimary,
      surfaceContainerLowest: black,
      surfaceContainerLow: Color(0xFF101010),
      surfaceContainer: surface,
      surfaceContainerHigh: surfaceHigh,
      surfaceContainerHighest: Color(0xFF242424),
      onSurfaceVariant: textSecondary,
      outline: charcoal,
      outlineVariant: Color(0xFF1E1E1E),
      inverseSurface: textPrimary,
      onInverseSurface: black,
      inversePrimary: greenDim,
      shadow: black,
      scrim: black,
    );
    final base = ThemeData(colorScheme: scheme, useMaterial3: true, brightness: Brightness.dark);
    final display = TextStyle(fontFamily: displayFamily, fontWeight: FontWeight.w600, fontStyle: FontStyle.italic, letterSpacing: 0.5, color: textPrimary);
    return base.copyWith(
      scaffoldBackgroundColor: ink,
      textTheme: base.textTheme.copyWith(
        headlineSmall: display.copyWith(fontSize: 28),
        headlineMedium: display.copyWith(fontSize: 34),
        titleLarge: display.copyWith(fontSize: 24),
        titleMedium: base.textTheme.titleMedium?.copyWith(fontFamily: displayFamily, fontWeight: FontWeight.w700, fontSize: 20, letterSpacing: 0.4),
        labelLarge: base.textTheme.labelLarge?.copyWith(fontFamily: displayFamily, fontWeight: FontWeight.w700, fontSize: 17, letterSpacing: 0.6),
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: black,
        foregroundColor: textPrimary,
        elevation: 0,
        centerTitle: false,
        titleTextStyle: display.copyWith(fontSize: 26),
      ),
      cardTheme: CardThemeData(
        color: surface,
        elevation: 0,
        margin: const EdgeInsets.symmetric(vertical: 4),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(6),
          side: const BorderSide(color: charcoal, width: 1),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: green,
          foregroundColor: black,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
          textStyle: const TextStyle(fontFamily: displayFamily, fontWeight: FontWeight.w700, fontSize: 18, letterSpacing: 0.8),
        ),
      ),
      textButtonTheme: TextButtonThemeData(style: TextButton.styleFrom(foregroundColor: green)),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: surface,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(6), borderSide: const BorderSide(color: charcoal)),
        enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(6), borderSide: const BorderSide(color: charcoal)),
        focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(6), borderSide: const BorderSide(color: green, width: 1.5)),
        labelStyle: const TextStyle(color: textSecondary),
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: black,
        indicatorColor: greenGlow,
        iconTheme: WidgetStateProperty.resolveWith((s) => IconThemeData(color: s.contains(WidgetState.selected) ? green : textSecondary)),
        labelTextStyle: WidgetStateProperty.resolveWith((s) => TextStyle(
            fontFamily: displayFamily, fontWeight: FontWeight.w700, fontSize: 14, letterSpacing: 0.5,
            color: s.contains(WidgetState.selected) ? green : textSecondary)),
      ),
      navigationRailTheme: NavigationRailThemeData(
        backgroundColor: black,
        indicatorColor: greenGlow,
        selectedIconTheme: const IconThemeData(color: green),
        unselectedIconTheme: const IconThemeData(color: textSecondary),
        selectedLabelTextStyle: const TextStyle(fontFamily: displayFamily, fontWeight: FontWeight.w700, color: green, letterSpacing: 0.5),
        unselectedLabelTextStyle: const TextStyle(fontFamily: displayFamily, fontWeight: FontWeight.w700, color: textSecondary, letterSpacing: 0.5),
      ),
      dividerTheme: const DividerThemeData(color: charcoal),
      snackBarTheme: const SnackBarThemeData(backgroundColor: surfaceHigh, contentTextStyle: TextStyle(color: textPrimary), actionTextColor: green),
      switchTheme: SwitchThemeData(
        thumbColor: WidgetStateProperty.resolveWith((s) => s.contains(WidgetState.selected) ? black : textSecondary),
        trackColor: WidgetStateProperty.resolveWith((s) => s.contains(WidgetState.selected) ? green : surfaceHigh),
      ),
      listTileTheme: const ListTileThemeData(iconColor: textSecondary),
      progressIndicatorTheme: const ProgressIndicatorThemeData(color: green),
    );
  }
}

/// Faint topographic-line backdrop used behind the sign-in screen.
class TopoBackground extends StatelessWidget {
  const TopoBackground({super.key, required this.child, this.opacity = 0.55});
  final Widget child;
  final double opacity;
  @override
  Widget build(BuildContext context) {
    return Stack(fit: StackFit.expand, children: [
      const ColoredBox(color: AmpBrand.black),
      Opacity(opacity: opacity, child: Image.asset(AmpBrand.topo, fit: BoxFit.cover, alignment: Alignment.center)),
      child,
    ]);
  }
}
