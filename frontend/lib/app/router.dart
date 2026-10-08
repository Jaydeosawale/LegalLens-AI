import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../core/widgets/app_role_shell.dart';
import '../features/workspace/presentation/workspace_pages.dart';
import '../features/workspace/presentation/document_analysis_page.dart';
import '../features/workspace/presentation/system_page.dart';
import '../features/advanced/presentation/advanced_research_page.dart';
import '../features/auth/presentation/auth_gate.dart';
import '../features/auth/presentation/login_page.dart';
import '../features/auth/presentation/register_page.dart';
import '../features/chat/presentation/chat_home_page.dart';
import '../features/knowledge_base/presentation/knowledge_base_page.dart';
import '../features/platform/presentation/platform_page.dart';
import '../features/users/presentation/users_page.dart';

final GoRouter appRouter = GoRouter(
  initialLocation: '/',

  routes: [
    GoRoute(
      path: '/monitoring',
      builder: (context, state) => const AppRoleShell(child: MonitoringPage()),
    ),
    GoRoute(
      path: '/system',
      builder: (context, state) => const AppRoleShell(child: SystemPage()),
    ),
    GoRoute(
      path: '/summary',
      builder: (context, state) => AppRoleShell(
        child: DocumentAnalysisPage(
          initialDocument: state.uri.queryParameters['document'],
        ),
      ),
    ),
    GoRoute(
      path: '/compare',
      builder: (context, state) =>
          const AppRoleShell(child: DocumentAnalysisPage(compare: true)),
    ),
    // =========================================================
    // AUTH GATE
    // =========================================================
    GoRoute(path: '/', builder: (context, state) => const AuthGate()),

    // =========================================================
    // LOGIN
    // =========================================================
    GoRoute(path: '/login', builder: (context, state) => const LoginPage()),

    // =========================================================
    // REGISTER
    // =========================================================
    GoRoute(
      path: '/register',
      builder: (context, state) => const RegisterPage(),
    ),

    // =========================================================
    // HOME
    // =========================================================
    GoRoute(
      path: '/home',
      builder: (context, state) => const AppRoleShell(child: DashboardPage()),
    ),

    // =========================================================
    // CHAT
    // =========================================================
    GoRoute(
      path: '/chat',
      builder: (context, state) => AppRoleShell(
        child: ChatHomePage(
          key: ValueKey(state.uri.toString()),
          conversationId: state.uri.queryParameters['conversation'],
          initialQuestion: state.uri.queryParameters['question'],
        ),
      ),
    ),

    // =========================================================
    // DOCUMENTS
    // =========================================================
    GoRoute(
      path: '/documents',
      builder: (context, state) =>
          const AppRoleShell(child: KnowledgeBasePage()),
    ),

    // =========================================================
    // HISTORY
    // =========================================================
    GoRoute(
      path: '/history',
      builder: (context, state) => const AppRoleShell(child: HistoryPage()),
    ),

    // =========================================================
    // ADVANCED RESEARCH
    // =========================================================
    GoRoute(
      path: '/advanced',
      builder: (context, state) =>
          const AppRoleShell(child: AdvancedResearchPage()),
    ),

    // =========================================================
    // ANALYTICS
    // =========================================================
    GoRoute(
      path: '/analytics',
      builder: (context, state) =>
          const AppRoleShell(child: DashboardPage(analytics: true)),
    ),

    // =========================================================
    // KNOWLEDGE BASE
    // =========================================================
    GoRoute(
      path: '/knowledge-base',
      builder: (context, state) =>
          const AppRoleShell(child: KnowledgeBasePage()),
    ),

    // =========================================================
    // PLATFORM
    // =========================================================
    GoRoute(
      path: '/platform',
      builder: (context, state) => const AppRoleShell(child: PlatformPage()),
    ),

    // =========================================================
    // USERS
    // =========================================================
    GoRoute(
      path: '/users',
      builder: (context, state) => const AppRoleShell(child: UsersPage()),
    ),

    // =========================================================
    // SETTINGS
    // =========================================================
    GoRoute(
      path: '/settings',
      builder: (context, state) => const AppRoleShell(child: AccountPage()),
    ),
  ],

  // ===========================================================
  // UNKNOWN ROUTE
  // ===========================================================
  errorBuilder: (context, state) => Scaffold(
    body: Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.search_off_rounded, size: 72),
            const SizedBox(height: 20),
            Text(
              'Page Not Found',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 10),
            const Text(
              'The page you are looking for does not exist '
              'or may have moved.',
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            FilledButton(
              onPressed: () => context.go('/'),
              child: const Text('Go to Home'),
            ),
          ],
        ),
      ),
    ),
  ),
);
