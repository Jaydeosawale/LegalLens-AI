import 'package:flutter/material.dart';

class AppColors {
  AppColors._();

  // ============================================================
  // BRAND — LEGAL INTELLIGENCE
  // ============================================================

  /// Primary LegalLens identity color.
  static const Color inkNavy = Color(0xFF182532);

  /// Alias used by existing widgets.
  static const Color legalNavy = inkNavy;

  /// Slightly lighter navy surface.
  static const Color slateNavy = Color(0xFF24384A);

  /// Light navy used for subtle surfaces and icons.
  static const Color legalNavyLight = Color(0xFFE8EEF2);

  /// Premium legal accent.
  static const Color antiqueGold = Color(0xFFC6A15B);

  /// Light premium gold background.
  static const Color antiqueGoldLight = Color(0xFFF3E9D5);

  /// Softer gold surface.
  static const Color softGold = antiqueGoldLight;

  /// Muted gold for subtle details.
  static const Color mutedGold = Color(0xFFD8BD84);

  // ============================================================
  // BACKGROUNDS
  // ============================================================

  /// Main application background.
  static const Color background = Color(0xFFF3F1EC);

  /// Main AI workspace.
  static const Color workspace = Color(0xFFF3F1EC);

  /// Slightly elevated workspace surface.
  static const Color workspaceBackground = Color(0xFFEDEBE6);

  /// Main cards and surfaces.
  static const Color surface = Color(0xFFFFFEFA);

  /// Muted card surface.
  static const Color surfaceMuted = Color(0xFFF8F6F1);

  /// Conversation history panel.
  static const Color conversationPanel = Color(0xFFF7F6F2);

  // ============================================================
  // TEXT
  // ============================================================

  static const Color textPrimary = Color(0xFF1D2A35);

  static const Color textSecondary = Color(0xFF66727C);

  static const Color textMuted = Color(0xFF89939B);

  static const Color textOnDark = Color(0xFFF7F4EE);

  static const Color textOnDarkMuted = Color(0xFFAEB9C2);

  // ============================================================
  // BORDERS
  // ============================================================

  /// Standard application border.
  static const Color border = Color(0xFFDCD8D0);

  /// Light border for cards and subtle separation.
  static const Color borderLight = Color(0xFFE9E5DE);

  /// Dark border for dark surfaces.
  static const Color borderDark = Color(0xFF324452);

  /// Border used by chat sidebar and conversation panels.
  static const Color sidebarBorder = Color(0xFFDCD8D0);

  // ============================================================
  // NAVIGATION
  // ============================================================

  static const Color sidebarBackground = inkNavy;

  static const Color sidebarSurface = Color(0xFF202F3D);

  static const Color sidebarSelected = Color(0xFF314354);

  static const Color sidebarHover = Color(0xFF293B4A);

  // ============================================================
  // CONVERSATIONS
  // ============================================================

  /// Selected conversation background.
  static const Color selectedConversation = Color(0xFFE5E9E8);

  /// Hover / inactive conversation surface.
  static const Color hoverConversation = Color(0xFFEFEEE9);

  // ============================================================
  // STATUS
  // ============================================================

  static const Color success = Color(0xFF2F7D5B);

  static const Color warning = Color(0xFFC58A2B);

  static const Color error = Color(0xFFB84A4A);

  static const Color info = Color(0xFF3C6E91);
}
