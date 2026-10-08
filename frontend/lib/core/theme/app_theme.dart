import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'app_colors.dart';

class AppTheme {
  AppTheme._();

  static final ThemeData lightTheme = ThemeData(
    useMaterial3: true,

    // ==========================================================
    // COLOR SCHEME
    // ==========================================================
    colorScheme: const ColorScheme.light(
      primary: AppColors.inkNavy,
      onPrimary: AppColors.textOnDark,

      secondary: AppColors.antiqueGold,
      onSecondary: AppColors.inkNavy,

      surface: AppColors.surface,
      onSurface: AppColors.textPrimary,

      error: AppColors.error,
      onError: Colors.white,
    ),

    // ==========================================================
    // MAIN BACKGROUND
    // ==========================================================
    scaffoldBackgroundColor: AppColors.background,

    // ==========================================================
    // TYPOGRAPHY
    // ==========================================================
    textTheme: GoogleFonts.interTextTheme().copyWith(
      displayLarge: GoogleFonts.inter(
        fontSize: 40,
        fontWeight: FontWeight.w700,
        color: AppColors.textPrimary,
        letterSpacing: -1.2,
      ),

      displayMedium: GoogleFonts.inter(
        fontSize: 32,
        fontWeight: FontWeight.w700,
        color: AppColors.textPrimary,
        letterSpacing: -0.8,
      ),

      headlineLarge: GoogleFonts.inter(
        fontSize: 28,
        fontWeight: FontWeight.w700,
        color: AppColors.textPrimary,
        letterSpacing: -0.5,
      ),

      headlineMedium: GoogleFonts.inter(
        fontSize: 24,
        fontWeight: FontWeight.w700,
        color: AppColors.textPrimary,
      ),

      headlineSmall: GoogleFonts.inter(
        fontSize: 20,
        fontWeight: FontWeight.w700,
        color: AppColors.textPrimary,
      ),

      titleLarge: GoogleFonts.inter(
        fontSize: 18,
        fontWeight: FontWeight.w700,
        color: AppColors.textPrimary,
      ),

      titleMedium: GoogleFonts.inter(
        fontSize: 16,
        fontWeight: FontWeight.w600,
        color: AppColors.textPrimary,
      ),

      titleSmall: GoogleFonts.inter(
        fontSize: 14,
        fontWeight: FontWeight.w600,
        color: AppColors.textPrimary,
      ),

      bodyLarge: GoogleFonts.inter(
        fontSize: 16,
        fontWeight: FontWeight.w400,
        color: AppColors.textPrimary,
        height: 1.5,
      ),

      bodyMedium: GoogleFonts.inter(
        fontSize: 14,
        fontWeight: FontWeight.w400,
        color: AppColors.textSecondary,
        height: 1.5,
      ),

      bodySmall: GoogleFonts.inter(
        fontSize: 12,
        fontWeight: FontWeight.w400,
        color: AppColors.textMuted,
        height: 1.4,
      ),

      labelLarge: GoogleFonts.inter(
        fontSize: 14,
        fontWeight: FontWeight.w600,
        color: AppColors.textPrimary,
      ),
    ),

    // ==========================================================
    // APP BAR
    // ==========================================================
    appBarTheme: AppBarTheme(
      elevation: 0,
      scrolledUnderElevation: 0,
      backgroundColor: AppColors.surface,
      foregroundColor: AppColors.textPrimary,
      surfaceTintColor: Colors.transparent,

      titleTextStyle: GoogleFonts.inter(
        fontSize: 18,
        fontWeight: FontWeight.w700,
        color: AppColors.textPrimary,
      ),

      iconTheme: const IconThemeData(color: AppColors.inkNavy),
    ),

    // ==========================================================
    // CARDS
    // ==========================================================
    cardTheme: CardThemeData(
      color: AppColors.surface,
      surfaceTintColor: Colors.transparent,
      elevation: 0,
      margin: EdgeInsets.zero,

      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(18),
        side: const BorderSide(color: AppColors.borderLight),
      ),
    ),

    // ==========================================================
    // DIVIDERS
    // ==========================================================
    dividerTheme: const DividerThemeData(
      color: AppColors.borderLight,
      thickness: 1,
      space: 1,
    ),

    // ==========================================================
    // INPUTS
    // ==========================================================
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: AppColors.surface,

      hintStyle: GoogleFonts.inter(color: AppColors.textMuted, fontSize: 14),

      contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),

      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(14),
        borderSide: const BorderSide(color: AppColors.border),
      ),

      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(14),
        borderSide: const BorderSide(color: AppColors.border),
      ),

      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(14),
        borderSide: const BorderSide(color: AppColors.antiqueGold, width: 1.5),
      ),
    ),

    // ==========================================================
    // BUTTONS
    // ==========================================================
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        elevation: 0,

        backgroundColor: AppColors.inkNavy,
        foregroundColor: AppColors.textOnDark,

        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 15),

        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),

        textStyle: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w600),
      ),
    ),

    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: AppColors.inkNavy,

        side: const BorderSide(color: AppColors.border),

        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 15),

        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    ),

    // ==========================================================
    // ICONS
    // ==========================================================
    iconTheme: const IconThemeData(color: AppColors.textSecondary),

    // ==========================================================
    // TOOLTIP
    // ==========================================================
    tooltipTheme: TooltipThemeData(
      decoration: BoxDecoration(
        color: AppColors.inkNavy,
        borderRadius: BorderRadius.circular(8),
      ),

      textStyle: GoogleFonts.inter(color: Colors.white, fontSize: 12),
    ),
  );
}
