import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:frontend_flutter/core/auth/user_role.dart';
import 'package:frontend_flutter/core/navigation/navigation_config.dart';
import 'package:frontend_flutter/core/widgets/app_role_shell.dart';
import 'package:frontend_flutter/features/auth/presentation/auth_gate.dart';
import 'package:frontend_flutter/features/auth/providers/auth_provider.dart';
import 'package:frontend_flutter/features/platform/providers/platform_permissions_provider.dart';
import 'role_access_test.dart' show TestAuth, TestPermissions;

class FailedLoginAuth extends AuthNotifier {
  @override
  AuthState build() => const AuthState(isLoading: false);
  @override
  Future<void> signIn({required String email, required String password}) async {
    state = const AuthState(isLoading: true);
    await Future<void>.delayed(Duration.zero);
    state = const AuthState(
      isLoading: false,
      errorMessage: 'Incorrect email or password.',
    );
    throw Exception('Invalid credentials');
  }
}

void main() {
  test('Normal user has no Dashboard navigation', () {
    expect(
      NavigationConfig.forRole(
        UserRole.user,
      ).any((item) => item.route == '/home'),
      isFalse,
    );
    expect(
      NavigationConfig.forRole(
        UserRole.admin,
      ).any((item) => item.route == '/home'),
      isTrue,
    );
  });
  for (final role in [UserRole.user, UserRole.admin, UserRole.superAdmin]) {
    testWidgets('${role.name} receives the correct landing screen', (
      tester,
    ) async {
      final router = GoRouter(
        routes: [
          GoRoute(path: '/', builder: (_, _) => const AuthGate()),
          GoRoute(
            path: '/chat',
            builder: (_, _) => const Text('Assistant landing'),
          ),
          GoRoute(
            path: '/home',
            builder: (_, _) => const Text('Dashboard landing'),
          ),
        ],
      );
      await tester.pumpWidget(
        ProviderScope(
          overrides: [authProvider.overrideWith(() => TestAuth(role))],
          child: MaterialApp.router(routerConfig: router),
        ),
      );
      await tester.pumpAndSettle();
      expect(
        find.text(
          role == UserRole.user ? 'Assistant landing' : 'Dashboard landing',
        ),
        findsOneWidget,
      );
      router.dispose();
    });
  }
  testWidgets('Old normal-user Dashboard links redirect to assistant', (
    tester,
  ) async {
    final router = GoRouter(
      initialLocation: '/home',
      routes: [
        GoRoute(
          path: '/home',
          builder: (_, _) =>
              const AppRoleShell(child: Text('Hidden dashboard')),
        ),
        GoRoute(
          path: '/chat',
          builder: (_, _) => const Text('Assistant landing'),
        ),
      ],
    );
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authProvider.overrideWith(() => TestAuth(UserRole.user)),
          platformPermissionsProvider.overrideWith(TestPermissions.new),
        ],
        child: MaterialApp.router(routerConfig: router),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('Assistant landing'), findsOneWidget);
    expect(find.text('Hidden dashboard'), findsNothing);
    router.dispose();
  });
  testWidgets(
    'Failed sign-in preserves form and displays error popup repeatedly',
    (tester) async {
      final router = GoRouter(
        routes: [GoRoute(path: '/', builder: (_, _) => const AuthGate())],
      );
      await tester.pumpWidget(
        ProviderScope(
          overrides: [authProvider.overrideWith(FailedLoginAuth.new)],
          child: MaterialApp.router(routerConfig: router),
        ),
      );
      await tester.pumpAndSettle();
      await tester.enterText(
        find.byType(TextFormField).at(0),
        'user@example.com',
      );
      await tester.enterText(
        find.byType(TextFormField).at(1),
        'incorrect-password',
      );
      for (var attempt = 0; attempt < 2; attempt++) {
        await tester.ensureVisible(find.text('Sign In'));
        await tester.tap(find.text('Sign In'));
        await tester.pumpAndSettle();
        expect(find.byType(AlertDialog), findsOneWidget);
        expect(find.text('Incorrect email or password.'), findsOneWidget);
        await tester.tap(find.text('OK'));
        await tester.pumpAndSettle();
        expect(find.text('user@example.com'), findsOneWidget);
      }
      expect(tester.takeException(), isNull);
      router.dispose();
    },
  );
}
