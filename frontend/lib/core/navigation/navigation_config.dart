import 'package:flutter/material.dart';

import '../auth/user_role.dart';
import 'navigation_item.dart';

class NavigationConfig {
  NavigationConfig._();

  static const List<NavigationItem> items = [
    NavigationItem(
      label: 'Research Monitoring',
      icon: Icons.manage_search,
      route: '/monitoring',
      allowedRoles: [UserRole.admin, UserRole.superAdmin],
      platformModule: 'research_history',
    ),
    // =========================================================
    // DASHBOARD
    // =========================================================
    NavigationItem(
      label: 'Dashboard',
      icon: Icons.grid_view_rounded,
      route: '/home',
      allowedRoles: [
        UserRole.legalProfessional,
        UserRole.admin,
        UserRole.superAdmin,
      ],
      platformModule: 'dashboard',
    ),

    // =========================================================
    // LEGAL RESEARCH
    // =========================================================
    NavigationItem(
      label: 'Legal AI Assistant',
      icon: Icons.auto_awesome_rounded,
      route: '/chat',
      allowedRoles: [
        UserRole.user,
        UserRole.legalProfessional,
        UserRole.admin,
        UserRole.superAdmin,
      ],
    ),

    NavigationItem(
      label: 'Documents',
      icon: Icons.description_outlined,
      route: '/documents',
      allowedRoles: [
        UserRole.user,
        UserRole.legalProfessional,
        UserRole.admin,
        UserRole.superAdmin,
      ],
      platformModule: 'documents',
    ),

    NavigationItem(
      label: 'Research History',
      icon: Icons.history_outlined,
      route: '/history',
      allowedRoles: [
        UserRole.user,
        UserRole.legalProfessional,
        UserRole.admin,
        UserRole.superAdmin,
      ],
      platformModule: 'research_history',
    ),

    NavigationItem(
      label: 'Advanced Research',
      icon: Icons.manage_search_rounded,
      route: '/advanced',
      allowedRoles: [
        UserRole.legalProfessional,
        UserRole.admin,
        UserRole.superAdmin,
      ],
      platformModule: 'advanced_research',
    ),
    NavigationItem(
      label: 'Summary',
      icon: Icons.subject,
      route: '/summary',
      allowedRoles: [
        UserRole.user,
        UserRole.legalProfessional,
        UserRole.admin,
        UserRole.superAdmin,
      ],
    ),
    NavigationItem(
      label: 'Compare',
      icon: Icons.compare_arrows,
      route: '/compare',
      allowedRoles: [
        UserRole.legalProfessional,
        UserRole.admin,
        UserRole.superAdmin,
      ],
    ),
    NavigationItem(
      label: 'System Configuration',
      icon: Icons.tune,
      route: '/system',
      allowedRoles: [UserRole.admin, UserRole.superAdmin],
    ),

    // =========================================================
    // KNOWLEDGE MANAGEMENT
    // =========================================================
    NavigationItem(
      label: 'Knowledge Base',
      icon: Icons.account_tree_outlined,
      route: '/knowledge-base',
      allowedRoles: [UserRole.admin, UserRole.superAdmin],
      platformModule: 'knowledge_base',
    ),

    // =========================================================
    // ADMINISTRATION
    // =========================================================
    NavigationItem(
      label: 'Analytics',
      icon: Icons.analytics_outlined,
      route: '/analytics',
      allowedRoles: [UserRole.admin, UserRole.superAdmin],
      platformModule: 'analytics',
    ),

    NavigationItem(
      label: 'Users',
      icon: Icons.people_outline_rounded,
      route: '/users',
      allowedRoles: [UserRole.admin, UserRole.superAdmin],
      platformModule: 'users',
    ),

    // =========================================================
    // PLATFORM
    // =========================================================
    NavigationItem(
      label: 'Platform',
      icon: Icons.admin_panel_settings_outlined,
      route: '/platform',
      allowedRoles: [UserRole.superAdmin],
    ),

    // =========================================================
    // SETTINGS
    // =========================================================
    NavigationItem(
      label: 'Settings',
      icon: Icons.settings_outlined,
      route: '/settings',
      allowedRoles: [
        UserRole.user,
        UserRole.legalProfessional,
        UserRole.admin,
        UserRole.superAdmin,
      ],
    ),
  ];

  static List<NavigationItem> forRole(UserRole role) {
    return items.where((item) => item.allowedRoles.contains(role)).toList();
  }
}
