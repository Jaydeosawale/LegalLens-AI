import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/platform_permissions_provider.dart';

class PlatformPage extends ConsumerWidget {
  const PlatformPage({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(platformPermissionsProvider);
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    'Admin Permissions',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                ),
                IconButton(
                  tooltip: 'Refresh permissions',
                  onPressed: state.isLoading
                      ? null
                      : () => ref
                            .read(platformPermissionsProvider.notifier)
                            .refresh(),
                  icon: const Icon(Icons.refresh),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (state.errorMessage != null)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 12),
                child: Text('Unable to update permissions. Please try again.'),
              ),
            if (state.isLoading)
              const Expanded(child: Center(child: CircularProgressIndicator()))
            else
              Expanded(
                child: ListView.separated(
                  itemCount: state.permissions.length,
                  separatorBuilder: (_, _) => const Divider(height: 1),
                  itemBuilder: (context, index) {
                    final permission = state.permissions[index];
                    return SwitchListTile(
                      title: Text(permission.moduleName.replaceAll('_', ' ')),
                      value: permission.enabledForAdmin,
                      onChanged: (enabled) async {
                        try {
                          await ref
                              .read(platformPermissionsProvider.notifier)
                              .updatePermission(
                                moduleName: permission.moduleName,
                                enabledForAdmin: enabled,
                              );
                        } catch (_) {
                          if (context.mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Unable to update permission.'),
                              ),
                            );
                          }
                        }
                      },
                    );
                  },
                ),
              ),
          ],
        ),
      ),
    );
  }
}
