import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../auth/user_role.dart';
import '../navigation/navigation_item.dart';
import '../theme/app_colors.dart';

import '../../features/auth/providers/auth_provider.dart';

class AppNavigationDrawer extends ConsumerWidget {
  const AppNavigationDrawer({super.key, required this.navigationItems});

  final List<NavigationItem> navigationItems;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final location = GoRouterState.of(context).uri.path;

    // ============================================================
    // AUTH USER
    // ============================================================

    final authState = ref.watch(authProvider);
    final user = authState.user;

    final fullName = user?.fullName?.trim() ?? '';
    final email = user?.email.trim() ?? '';

    final displayName = fullName.isNotEmpty
        ? fullName
        : email.isNotEmpty
        ? email
        : 'Legal Lens User';

    final initial = displayName.isNotEmpty
        ? displayName.substring(0, 1).toUpperCase()
        : 'U';

    final roleLabel = _getRoleLabel(user?.role);

    return Drawer(
      width: MediaQuery.sizeOf(context).width * 0.84,
      backgroundColor: AppColors.background,
      elevation: 18,
      child: SafeArea(
        child: Column(
          children: [
            // ============================================================
            // BRAND HEADER
            // ============================================================

            Container(
              width: double.infinity,
              padding: const EdgeInsets.fromLTRB(20, 18, 20, 18),
              decoration: BoxDecoration(
                color: AppColors.surface,
                border: Border(
                  bottom: BorderSide(
                    color: AppColors.borderLight.withValues(alpha: 0.8),
                  ),
                ),
              ),
              child: Row(
                children: [
                  Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      color: AppColors.antiqueGoldLight,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(
                        color: AppColors.antiqueGold.withValues(alpha: 0.18),
                      ),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(7),
                      child: Image.asset(
                        'assets/images/legallens_logo.png',
                        fit: BoxFit.contain,
                      ),
                    ),
                  ),

                  const SizedBox(width: 14),

                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Legal Lens',
                          style: TextStyle(
                            color: AppColors.textPrimary,
                            fontSize: 19,
                            fontWeight: FontWeight.w700,
                            letterSpacing: -0.2,
                          ),
                        ),

                        SizedBox(height: 3),

                        Text(
                          'LEGAL INTELLIGENCE',
                          style: TextStyle(
                            color: AppColors.textSecondary,
                            fontSize: 9,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 1.1,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            // ============================================================
            // NAVIGATION
            // ============================================================
            Expanded(
              child: ListView(
                padding: const EdgeInsets.fromLTRB(12, 18, 12, 12),
                children: [
                  const Padding(
                    padding: EdgeInsets.only(left: 10, bottom: 10),
                    child: Text(
                      'WORKSPACE',
                      style: TextStyle(
                        color: AppColors.textSecondary,
                        fontSize: 10,
                        fontWeight: FontWeight.w700,
                        letterSpacing: 1.1,
                      ),
                    ),
                  ),

                  ...navigationItems.map((item) {
                    final selected =
                        location == item.route ||
                        (item.route == '/home' && location == '/');

                    return _MobileNavigationTile(
                      item: item,
                      selected: selected,
                    );
                  }),
                ],
              ),
            ),

            // ============================================================
            // FOOTER DIVIDER
            // ============================================================
            const Divider(height: 1, color: AppColors.borderLight),

            // ============================================================
            // USER PROFILE
            // ============================================================
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 14, 16, 16),
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppColors.surface,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: AppColors.borderLight),
                ),
                child: Row(
                  children: [
                    // ====================================================
                    // AVATAR
                    // ====================================================

                    Container(
                      width: 42,
                      height: 42,
                      alignment: Alignment.center,
                      decoration: BoxDecoration(
                        color: AppColors.antiqueGold,
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: AppColors.antiqueGold.withValues(
                              alpha: 0.18,
                            ),
                            blurRadius: 10,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: Text(
                        initial,
                        style: const TextStyle(
                          color: AppColors.inkNavy,
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),

                    const SizedBox(width: 12),

                    // ====================================================
                    // USER DETAILS
                    // ====================================================
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            displayName,
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
                            roleLabel,
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

                    // ====================================================
                    // ACCOUNT MENU
                    // ====================================================
                    PopupMenuButton<String>(
                      tooltip: 'Account options',
                      padding: EdgeInsets.zero,
                      icon: const Icon(
                        Icons.more_horiz_rounded,
                        size: 21,
                        color: AppColors.textSecondary,
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(14),
                      ),
                      onSelected: (value) async {
                        if (value == 'profile') {
                          _showProfileDialog(
                            context,
                            displayName: displayName,
                            email: email,
                            role: roleLabel,
                          );
                        }

                        if (value == 'logout') {
                          Navigator.of(context).pop();

                          await ref.read(authProvider.notifier).logout();
                        }
                      },
                      itemBuilder: (context) => [
                        const PopupMenuItem<String>(
                          value: 'profile',
                          child: Row(
                            children: [
                              Icon(
                                Icons.person_outline_rounded,
                                color: AppColors.textSecondary,
                              ),
                              SizedBox(width: 10),
                              Text('Profile'),
                            ],
                          ),
                        ),

                        const PopupMenuDivider(),

                        const PopupMenuItem<String>(
                          value: 'logout',
                          child: Row(
                            children: [
                              Icon(
                                Icons.logout_rounded,
                                color: AppColors.textSecondary,
                              ),
                              SizedBox(width: 10),
                              Text('Logout'),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ============================================================
  // ROLE LABEL
  // ============================================================

  String _getRoleLabel(UserRole? role) {
    switch (role) {
      case UserRole.superAdmin:
        return 'Super Administrator';

      case UserRole.admin:
        return 'Administrator';

      case UserRole.user:
      case UserRole.legalProfessional:
        return 'Legal Lens User';

      case null:
        return 'Legal Lens User';
    }
  }

  // ============================================================
  // PROFILE DIALOG
  // ============================================================

  void _showProfileDialog(
    BuildContext context, {
    required String displayName,
    required String email,
    required String role,
  }) {
    showDialog<void>(
      context: context,
      builder: (context) {
        return AlertDialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
          title: const Text(
            'Profile',
            style: TextStyle(
              color: AppColors.textPrimary,
              fontWeight: FontWeight.w700,
            ),
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                displayName,
                style: const TextStyle(
                  color: AppColors.textPrimary,
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                ),
              ),

              const SizedBox(height: 8),

              if (email.isNotEmpty)
                Text(
                  email,
                  style: const TextStyle(
                    color: AppColors.textSecondary,
                    fontSize: 13,
                  ),
                ),

              const SizedBox(height: 8),

              Text(
                role,
                style: const TextStyle(
                  color: AppColors.textSecondary,
                  fontSize: 13,
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              child: const Text('Close'),
            ),
          ],
        );
      },
    );
  }
}

// ================================================================
// MOBILE NAVIGATION TILE
// ================================================================

class _MobileNavigationTile extends StatelessWidget {
  const _MobileNavigationTile({required this.item, required this.selected});

  final NavigationItem item;
  final bool selected;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 5),
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(13),
        child: InkWell(
          borderRadius: BorderRadius.circular(13),
          onTap: () {
            Navigator.pop(context);
            context.go(item.route);
          },
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 180),
            padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 13),
            decoration: BoxDecoration(
              color: selected ? AppColors.inkNavy : Colors.transparent,
              borderRadius: BorderRadius.circular(13),
            ),
            child: Row(
              children: [
                // ========================================================
                // ICON
                // ========================================================

                Container(
                  width: 38,
                  height: 38,
                  alignment: Alignment.center,
                  decoration: BoxDecoration(
                    color: selected
                        ? AppColors.antiqueGold.withValues(alpha: 0.12)
                        : AppColors.surface,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(
                    item.icon,
                    size: 20,
                    color: selected
                        ? AppColors.antiqueGold
                        : AppColors.textSecondary,
                  ),
                ),

                const SizedBox(width: 13),

                // ========================================================
                // LABEL
                // ========================================================
                Expanded(
                  child: Text(
                    item.label,
                    style: TextStyle(
                      color: selected ? Colors.white : AppColors.textSecondary,
                      fontSize: 14,
                      fontWeight: selected ? FontWeight.w600 : FontWeight.w500,
                    ),
                  ),
                ),

                // ========================================================
                // ACTIVE INDICATOR
                // ========================================================
                if (selected)
                  const Icon(
                    Icons.chevron_right_rounded,
                    size: 20,
                    color: Colors.white,
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
