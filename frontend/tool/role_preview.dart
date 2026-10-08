import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend_flutter/app/router.dart';
import 'package:frontend_flutter/core/auth/user_role.dart';
import 'package:frontend_flutter/core/theme/app_theme.dart';
import 'package:frontend_flutter/features/auth/providers/auth_provider.dart';
import 'package:frontend_flutter/features/chat/providers/chat_providers.dart';
import 'preview_support.dart';

void main() {
  final api = PreviewApi();
  runApp(
    ProviderScope(
      overrides: [
        authProvider.overrideWith(PreviewAuth.new),
        dioProvider.overrideWithValue(api.create()),
        firebaseAuthServiceProvider.overrideWithValue(PreviewFirebaseService()),
      ],
      child: const RolePreview(),
    ),
  );
}

class RolePreview extends ConsumerWidget {
  const RolePreview({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) => MaterialApp.router(
    theme: AppTheme.lightTheme,
    routerConfig: appRouter,
    builder: (context, child) => Column(
      children: [
        Material(
          color: Colors.white,
          child: SafeArea(
            bottom: false,
            child: Padding(
              padding: const EdgeInsets.all(8),
              child: Column(
                children: [
                  const Text(
                    'Screen preview | sample data',
                    style: TextStyle(fontSize: 12),
                  ),
                  const SizedBox(height: 4),
                  SizedBox(
                    width: 360,
                    child: SegmentedButton<UserRole>(
                      showSelectedIcon: false,
                      style: const ButtonStyle(
                        padding: WidgetStatePropertyAll(
                          EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                        ),
                        textStyle: WidgetStatePropertyAll(
                          TextStyle(fontSize: 14),
                        ),
                      ),
                      segments: const [
                        ButtonSegment(
                          value: UserRole.user,
                          label: Text('User'),
                        ),
                        ButtonSegment(
                          value: UserRole.legalProfessional,
                          label: Text('Lawyer'),
                        ),
                        ButtonSegment(
                          value: UserRole.admin,
                          label: Text('Admin'),
                        ),
                        ButtonSegment(
                          value: UserRole.superAdmin,
                          label: Text('Owner'),
                        ),
                      ],
                      selected: {ref.watch(previewRoleProvider)},
                      onSelectionChanged: (roles) {
                        ref
                            .read(previewRoleProvider.notifier)
                            .select(roles.first);
                        appRouter.go('/home');
                      },
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
        Expanded(child: child ?? const SizedBox()),
      ],
    ),
  );
}
