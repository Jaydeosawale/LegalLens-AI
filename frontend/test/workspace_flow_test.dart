import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend_flutter/app/router.dart';
import 'package:frontend_flutter/core/auth/user_role.dart';
import 'package:frontend_flutter/core/navigation/navigation_config.dart';
import 'package:frontend_flutter/features/auth/providers/auth_provider.dart';
import 'package:frontend_flutter/features/chat/providers/chat_providers.dart';
import '../tool/preview_support.dart';

class SelectedPreviewRole extends PreviewRole {
  SelectedPreviewRole(this.initialRole);
  final UserRole initialRole;
  @override
  UserRole build() => initialRole;
}

void main() {
  testWidgets('All role workspaces render at desktop and mobile sizes', (
    tester,
  ) async {
    for (final size in [const Size(1440, 1000), const Size(390, 844)]) {
      tester.view.physicalSize = size;
      tester.view.devicePixelRatio = 1;
      for (final role in UserRole.values) {
        final api = PreviewApi();
        final container = ProviderContainer(
          overrides: [
            previewRoleProvider.overrideWith(() => SelectedPreviewRole(role)),
            authProvider.overrideWith(PreviewAuth.new),
            dioProvider.overrideWithValue(api.create()),
            firebaseAuthServiceProvider.overrideWithValue(
              PreviewFirebaseService(),
            ),
          ],
        );
        appRouter.go('/home');
        await tester.pumpWidget(
          UncontrolledProviderScope(
            container: container,
            child: MaterialApp.router(routerConfig: appRouter),
          ),
        );
        await tester.pumpAndSettle();
        expect(
          tester.takeException(),
          isNull,
          reason: '$role dashboard at $size',
        );
        for (final item in NavigationConfig.forRole(role)) {
          appRouter.go(item.route);
          await tester.pumpAndSettle();
          expect(
            tester.takeException(),
            isNull,
            reason: '$role ${item.route} at $size',
          );
          expect(
            find.text('This section is unavailable for your account.'),
            findsNothing,
            reason: '$role ${item.route}',
          );
        }
        if (role == UserRole.user) {
          appRouter.go('/compare');
          await tester.pumpAndSettle();
          expect(
            find.text('This section is unavailable for your account.'),
            findsOneWidget,
          );
        }
        await tester.pumpWidget(const SizedBox());
        container.dispose();
      }
    }
    tester.view.resetPhysicalSize();
    tester.view.resetDevicePixelRatio();
  });

  testWidgets(
    'Summary and comparison display generated answers and citations',
    (tester) async {
      final api = PreviewApi();
      final container = ProviderContainer(
        overrides: [
          previewRoleProvider.overrideWith(
            () => SelectedPreviewRole(UserRole.legalProfessional),
          ),
          authProvider.overrideWith(PreviewAuth.new),
          dioProvider.overrideWithValue(api.create()),
        ],
      );
      appRouter.go('/summary');
      await tester.pumpWidget(
        UncontrolledProviderScope(
          container: container,
          child: MaterialApp.router(routerConfig: appRouter),
        ),
      );
      await tester.pumpAndSettle();
      await tester.tap(find.byType(CheckboxListTile).first);
      await tester.pumpAndSettle();
      await tester.tap(find.text('Generate summary'));
      await tester.pumpAndSettle();
      await tester.drag(find.byType(ListView).last, const Offset(0, -400));
      await tester.pumpAndSettle();
      expect(find.textContaining('Rental Agreement.pdf, p. 3'), findsOneWidget);
      appRouter.go('/compare');
      await tester.pumpAndSettle();
      await tester.tap(find.byType(CheckboxListTile).first);
      await tester.tap(find.byType(CheckboxListTile).last);
      await tester.pumpAndSettle();
      await tester.tap(find.widgetWithText(FilledButton, 'Compare'));
      await tester.pumpAndSettle();
      await tester.drag(find.byType(ListView).last, const Offset(0, -400));
      await tester.pumpAndSettle();
      expect(find.textContaining('Rental Agreement.pdf, p. 3'), findsOneWidget);
      expect(tester.takeException(), isNull);
      await tester.pumpWidget(const SizedBox());
      container.dispose();
    },
  );
}
