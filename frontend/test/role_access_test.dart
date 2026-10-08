import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:frontend_flutter/core/auth/user_role.dart';
import 'package:frontend_flutter/core/widgets/app_role_shell.dart';
import 'package:frontend_flutter/features/auth/models/app_user.dart';
import 'package:frontend_flutter/features/auth/providers/auth_provider.dart';
import 'package:frontend_flutter/features/chat/providers/chat_providers.dart';
import 'package:frontend_flutter/features/platform/models/platform_permission.dart';
import 'package:frontend_flutter/features/platform/providers/platform_permissions_provider.dart';
import 'package:frontend_flutter/features/users/presentation/users_page.dart';

class TestAuth extends AuthNotifier {
  TestAuth(this.role);
  final UserRole role;
  @override
  AuthState build() => AuthState(
    isLoading: false,
    user: AppUser(
      id: 'current',
      email: 'current@example.com',
      fullName: 'Current',
      role: role,
    ),
  );
}

class TestPermissions extends PlatformPermissionsNotifier {
  @override
  PlatformPermissionsState build() => PlatformPermissionsState(
    permissions: [
      for (final module in [
        'dashboard',
        'documents',
        'research_history',
        'advanced_research',
        'knowledge_base',
        'analytics',
        'users',
      ])
        PlatformPermission(
          moduleName: module,
          enabledForAdmin: true,
          updatedAt: DateTime(2026),
        ),
    ],
  );
}

void main() {
  for (final role in UserRole.values) {
    testWidgets('${role.name}: controls and direct page access', (
      tester,
    ) async {
      final dio = Dio();
      dio.interceptors.add(
        InterceptorsWrapper(
          onRequest: (options, handler) {
            handler.resolve(
              Response(
                requestOptions: options,
                data: [
                  {
                    'id': 'target',
                    'full_name': 'Normal User',
                    'email': 'user@example.com',
                    'role': 'user',
                    'is_active': true,
                  },
                ],
              ),
            );
          },
        ),
      );
      final router = GoRouter(
        initialLocation: '/users',
        routes: [
          GoRoute(
            path: '/users',
            builder: (_, _) => const AppRoleShell(child: UsersPage()),
          ),
          GoRoute(
            path: '/chat',
            builder: (_, _) =>
                const AppRoleShell(child: Text('Research workspace')),
          ),
        ],
      );
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            authProvider.overrideWith(() => TestAuth(role)),
            platformPermissionsProvider.overrideWith(TestPermissions.new),
            dioProvider.overrideWithValue(dio),
          ],
          child: MaterialApp.router(routerConfig: router),
        ),
      );
      await tester.pumpAndSettle();
      if (!role.isAdministrator) {
        expect(
          find.text('This section is unavailable for your account.'),
          findsOneWidget,
        );
        expect(find.text('Normal User'), findsNothing);
      } else {
        expect(find.text('Normal User'), findsOneWidget);
        expect(find.byTooltip('Manage user'), findsOneWidget);
      }
      expect(tester.takeException(), isNull);
      router.dispose();
    });
  }
}
