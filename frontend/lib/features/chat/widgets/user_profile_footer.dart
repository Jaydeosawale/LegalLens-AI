import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';

class UserProfileFooter extends StatelessWidget {
  const UserProfileFooter({
    super.key,
    required this.name,
    required this.role,
    required this.onLogout,
    this.initial,
  });

  final String name;
  final String role;
  final String? initial;

  final VoidCallback onLogout;

  @override
  Widget build(BuildContext context) {
    final avatarInitial =
        initial ?? (name.isNotEmpty ? name[0].toUpperCase() : 'U');

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.borderLight),
      ),
      child: Row(
        children: [
          // ============================================================
          // AVATAR
          // ============================================================

          Container(
            width: 42,
            height: 42,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: AppColors.antiqueGold,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: AppColors.antiqueGold.withValues(alpha: 0.18),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Text(
              avatarInitial,
              style: const TextStyle(
                color: AppColors.inkNavy,
                fontSize: 16,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),

          const SizedBox(width: 12),

          // ============================================================
          // USER DETAILS
          // ============================================================
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  name,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    color: AppColors.textPrimary,
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),

                const SizedBox(height: 3),

                Text(
                  role,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    color: AppColors.textSecondary,
                    fontSize: 11,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),

          // ============================================================
          // MORE MENU
          // ============================================================
          PopupMenuButton<_UserMenuAction>(
            tooltip: 'Account options',
            padding: EdgeInsets.zero,
            offset: const Offset(0, -150),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(14),
            ),
            color: AppColors.surface,
            elevation: 8,
            onSelected: (action) {
              switch (action) {
                case _UserMenuAction.profile:
                  // Future: Navigate to profile.
                  break;

                case _UserMenuAction.settings:
                  // Future: Navigate to settings.
                  break;

                case _UserMenuAction.logout:
                  onLogout();
                  break;
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: _UserMenuAction.profile,
                child: _MenuItem(
                  icon: Icons.person_outline_rounded,
                  label: 'Profile',
                ),
              ),

              const PopupMenuItem(
                value: _UserMenuAction.settings,
                child: _MenuItem(
                  icon: Icons.settings_outlined,
                  label: 'Settings',
                ),
              ),

              const PopupMenuDivider(),

              const PopupMenuItem(
                value: _UserMenuAction.logout,
                child: _MenuItem(
                  icon: Icons.logout_rounded,
                  label: 'Logout',
                  isLogout: true,
                ),
              ),
            ],
            child: Container(
              width: 36,
              height: 36,
              alignment: Alignment.center,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(
                Icons.more_horiz_rounded,
                size: 21,
                color: AppColors.textSecondary,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ======================================================================
// MENU ACTION
// ======================================================================

enum _UserMenuAction { profile, settings, logout }

// ======================================================================
// MENU ITEM
// ======================================================================

class _MenuItem extends StatelessWidget {
  const _MenuItem({
    required this.icon,
    required this.label,
    this.isLogout = false,
  });

  final IconData icon;
  final String label;
  final bool isLogout;

  @override
  Widget build(BuildContext context) {
    final color = isLogout ? Colors.red.shade700 : AppColors.textPrimary;

    return Row(
      children: [
        Icon(icon, size: 20, color: color),

        const SizedBox(width: 12),

        Text(
          label,
          style: TextStyle(
            color: color,
            fontSize: 14,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }
}
