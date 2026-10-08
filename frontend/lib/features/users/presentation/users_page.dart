import 'package:flutter/material.dart';
import '../../../core/auth/user_role.dart';
import '../../auth/providers/auth_provider.dart';
import '../../chat/providers/chat_providers.dart';
import '../../workspace/presentation/workspace_pages.dart';

class UsersPage extends StatelessWidget {
  const UsersPage({super.key});

  @override
  Widget build(BuildContext context) {
    return DataPage(
      title: 'Users',
      load: (dio) async => (await dio.get('/admin/users')).data,
      builder: (context, ref, data, refresh) {
        final rows = data as List;
        final superAdmin = ref.watch(authProvider).role == UserRole.superAdmin;
        return ListView.separated(
          itemCount: rows.length,
          separatorBuilder: (_, _) => const Divider(height: 1),
          itemBuilder: (context, index) {
            final row = rows[index] as Map;
            final protected =
                row['role'] == 'super_admin' ||
                (!superAdmin && row['role'] == 'admin');
            return ListTile(
              leading: const Icon(Icons.person_outline),
              title: Text(
                '${row['full_name']}',
                overflow: TextOverflow.ellipsis,
              ),
              subtitle: Text(
                '${row['email']}\n${row['role']} | ${row['is_active'] == true ? 'Active' : 'Disabled'}',
              ),
              isThreeLine: true,
              trailing: protected
                  ? null
                  : PopupMenuButton<String>(
                      tooltip: 'Manage user',
                      itemBuilder: (_) => [
                        const PopupMenuItem(
                          value: 'legal_professional',
                          child: Text('Change to legal professional'),
                        ),
                        if (superAdmin)
                          PopupMenuItem(
                            value: row['role'] == 'admin' ? 'user' : 'admin',
                            child: Text(
                              row['role'] == 'admin'
                                  ? 'Change to user'
                                  : 'Change to admin',
                            ),
                          ),
                        if (!superAdmin)
                          const PopupMenuItem(
                            value: 'user',
                            child: Text('Change to user'),
                          ),
                        PopupMenuItem(
                          value: 'status',
                          child: Text(
                            row['is_active'] == true
                                ? 'Disable account'
                                : 'Enable account',
                          ),
                        ),
                      ],
                      onSelected: (action) async {
                        final approved = await showDialog<bool>(
                          context: context,
                          builder: (context) => AlertDialog(
                            title: const Text('Update account?'),
                            content: Text(
                              action == 'status'
                                  ? 'Change access for ${row['email']}?'
                                  : 'Change ${row['email']} to $action?',
                            ),
                            actions: [
                              TextButton(
                                onPressed: () => Navigator.pop(context, false),
                                child: const Text('Cancel'),
                              ),
                              FilledButton(
                                onPressed: () => Navigator.pop(context, true),
                                child: const Text('Update'),
                              ),
                            ],
                          ),
                        );
                        if (approved != true) return;
                        try {
                          await ref
                              .read(dioProvider)
                              .put(
                                '/admin/users/${row['id']}/${action == 'status' ? 'status' : 'role'}',
                                data: action == 'status'
                                    ? {'is_active': row['is_active'] != true}
                                    : {'role': action},
                              );
                          refresh();
                        } catch (e) {
                          if (context.mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(content: Text(apiError(e))),
                            );
                          }
                        }
                      },
                    ),
            );
          },
        );
      },
    );
  }
}
