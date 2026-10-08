import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../auth/user_role.dart';
import '../navigation/navigation_item.dart';

import '../../features/auth/providers/auth_provider.dart';

class NavigationSidebar extends ConsumerWidget {
  const NavigationSidebar({super.key, required this.navigationItems});

  final List<NavigationItem> navigationItems;

  static const _sidebarColor = Color(0xFF17212B);
  static const _sidebarSecondary = Color(0xFF22303C);
  static const _gold = Color(0xFFB08D57);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final location = GoRouterState.of(context).uri.path;

    final authState = ref.watch(authProvider);

    final user = authState.user;
    final role = authState.role ?? UserRole.user;

    final userName = _getUserName(user);
    final roleLabel = _getRoleLabel(role);
    final initial = _getInitial(userName);

    return Container(
      width: 278,
      decoration: const BoxDecoration(
        color: _sidebarColor,
        border: Border(right: BorderSide(color: Color(0xFF2B3A46))),
      ),
      child: Column(
        children: [
          // =========================================================
          // BRAND
          // =========================================================

          Padding(
            padding: const EdgeInsets.fromLTRB(22, 28, 22, 24),
            child: Row(
              children: [
                Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: _gold,
                    borderRadius: BorderRadius.circular(13),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withValues(alpha: 0.18),
                        blurRadius: 12,
                        offset: const Offset(0, 5),
                      ),
                    ],
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(7),
                    child: Image.asset(
                      'assets/images/legallens_logo.png',
                      fit: BoxFit.contain,
                    ),
                  ),
                ),

                const SizedBox(width: 13),

                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Legal Lens',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 19,
                          fontWeight: FontWeight.w700,
                          letterSpacing: -0.4,
                        ),
                      ),

                      SizedBox(height: 2),

                      Text(
                        'INTELLIGENCE PLATFORM',
                        style: TextStyle(
                          color: Color(0xFF91A0AD),
                          fontSize: 9,
                          fontWeight: FontWeight.w600,
                          letterSpacing: 1.2,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 20),
            child: Divider(color: Color(0xFF2B3A46), height: 1),
          ),

          const SizedBox(height: 18),

          // =========================================================
          // NAVIGATION LABEL
          // =========================================================
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 22),
            child: Align(
              alignment: Alignment.centerLeft,
              child: Text(
                'WORKSPACE',
                style: TextStyle(
                  color: Color(0xFF7E8C99),
                  fontSize: 10,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 1.3,
                ),
              ),
            ),
          ),

          const SizedBox(height: 10),

          // =========================================================
          // NAVIGATION
          // =========================================================
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              itemCount: navigationItems.length,
              itemBuilder: (context, index) {
                final item = navigationItems[index];

                final selected =
                    location == item.route ||
                    (item.route == '/home' && location == '/');

                return _NavigationTile(item: item, selected: selected);
              },
            ),
          ),

          // =========================================================
          // USER AREA
          // =========================================================
          Container(
            margin: const EdgeInsets.fromLTRB(14, 8, 14, 16),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: _sidebarSecondary,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFF31414E)),
            ),
            child: Row(
              children: [
                // AVATAR

                Container(
                  width: 40,
                  height: 40,
                  decoration: const BoxDecoration(
                    color: _gold,
                    shape: BoxShape.circle,
                  ),
                  alignment: Alignment.center,
                  child: Text(
                    initial,
                    style: const TextStyle(
                      color: _sidebarColor,
                      fontSize: 15,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),

                const SizedBox(width: 11),

                // USER INFORMATION
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        userName,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                        ),
                      ),

                      const SizedBox(height: 3),

                      Text(
                        roleLabel,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          color: Color(0xFF9AA7B2),
                          fontSize: 11,
                        ),
                      ),
                    ],
                  ),
                ),

                // ACCOUNT MENU
                PopupMenuButton<String>(
                  tooltip: 'Account options',
                  color: const Color(0xFF22303C),
                  icon: const Icon(
                    Icons.more_horiz_rounded,
                    color: Color(0xFF9AA7B2),
                  ),
                  onSelected: (value) async {
                    switch (value) {
                      case 'profile':
                        break;

                      case 'settings':
                        context.go('/settings');
                        break;

                      case 'logout':
                        await ref.read(authProvider.notifier).logout();
                        break;
                    }
                  },
                  itemBuilder: (context) => const [
                    PopupMenuItem(
                      value: 'profile',
                      child: Row(
                        children: [
                          Icon(
                            Icons.person_outline_rounded,
                            color: Colors.white70,
                          ),
                          SizedBox(width: 10),
                          Text(
                            'Profile',
                            style: TextStyle(color: Colors.white),
                          ),
                        ],
                      ),
                    ),

                    PopupMenuItem(
                      value: 'settings',
                      child: Row(
                        children: [
                          Icon(Icons.settings_outlined, color: Colors.white70),
                          SizedBox(width: 10),
                          Text(
                            'Settings',
                            style: TextStyle(color: Colors.white),
                          ),
                        ],
                      ),
                    ),

                    PopupMenuDivider(),

                    PopupMenuItem(
                      value: 'logout',
                      child: Row(
                        children: [
                          Icon(Icons.logout_rounded, color: Colors.redAccent),
                          SizedBox(width: 10),
                          Text(
                            'Logout',
                            style: TextStyle(
                              color: Colors.redAccent,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ============================================================
// NAVIGATION TILE
// ============================================================

class _NavigationTile extends StatelessWidget {
  const _NavigationTile({required this.item, required this.selected});

  final NavigationItem item;
  final bool selected;

  static const _gold = Color(0xFFB08D57);

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 5),
      decoration: BoxDecoration(
        color: selected ? const Color(0xFF2A3946) : Colors.transparent,
        borderRadius: BorderRadius.circular(12),
        border: selected
            ? const Border(left: BorderSide(color: _gold, width: 3))
            : null,
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => context.go(item.route),
        hoverColor: const Color(0xFF273642),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 13),
          child: Row(
            children: [
              Icon(
                item.icon,
                size: 21,
                color: selected
                    ? const Color(0xFFD6B982)
                    : const Color(0xFF9AA7B2),
              ),

              const SizedBox(width: 14),

              Expanded(
                child: Text(
                  item.label,
                  style: TextStyle(
                    color: selected ? Colors.white : const Color(0xFFC0C8CF),
                    fontSize: 14,
                    fontWeight: selected ? FontWeight.w600 : FontWeight.w500,
                  ),
                ),
              ),

              if (selected)
                const Icon(
                  Icons.arrow_forward_ios_rounded,
                  size: 12,
                  color: _gold,
                ),
            ],
          ),
        ),
      ),
    );
  }
}

// ============================================================
// USER HELPERS
// ============================================================

String _getUserName(dynamic user) {
  if (user == null) {
    return 'User';
  }

  final displayName = user.fullName;

  if (displayName != null && displayName.toString().trim().isNotEmpty) {
    return displayName.toString().trim();
  }

  final email = user.email;

  if (email != null && email.toString().trim().isNotEmpty) {
    return email.toString().split('@').first;
  }

  return 'User';
}

String _getInitial(String name) {
  if (name.trim().isEmpty) {
    return 'U';
  }

  return name.trim().substring(0, 1).toUpperCase();
}

String _getRoleLabel(UserRole role) {
  switch (role) {
    case UserRole.superAdmin:
      return 'Super Admin';

    case UserRole.admin:
      return 'Administrator';

    case UserRole.user:
      return 'Legal Lens User';
    case UserRole.legalProfessional:
      return 'Legal Professional';
  }
}
