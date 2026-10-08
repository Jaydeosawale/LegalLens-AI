import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/auth/user_role.dart';
import '../../auth/providers/auth_provider.dart';
import '../../chat/providers/chat_providers.dart';

String apiError(Object error) {
  if (error is DioException) {
    final data = error.response?.data;
    if (data is Map && data['detail'] is String) return data['detail'];
    if (error.response?.statusCode == 403) {
      return 'You do not have access to this section.';
    }
  }
  return 'Unable to load data. Please try again.';
}

class DataPage extends ConsumerStatefulWidget {
  const DataPage({
    super.key,
    required this.title,
    required this.load,
    required this.builder,
  });
  final String title;
  final Future<dynamic> Function(Dio dio) load;
  final Widget Function(BuildContext, WidgetRef, dynamic, VoidCallback) builder;

  @override
  ConsumerState<DataPage> createState() => _DataPageState();
}

class _DataPageState extends ConsumerState<DataPage> {
  late Future<dynamic> _future;
  @override
  void initState() {
    super.initState();
    _reload();
  }

  void _reload() {
    _future = widget.load(ref.read(dioProvider));
  }

  void _refresh() {
    setState(_reload);
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    body: Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  widget.title,
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
              ),
              IconButton(
                tooltip: 'Refresh',
                onPressed: _refresh,
                icon: const Icon(Icons.refresh),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Expanded(
            child: FutureBuilder<dynamic>(
              future: _future,
              builder: (context, snapshot) {
                if (snapshot.connectionState != ConnectionState.done) {
                  return const Center(child: CircularProgressIndicator());
                }
                if (snapshot.hasError) {
                  return Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          apiError(snapshot.error!),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 12),
                        TextButton.icon(
                          onPressed: _refresh,
                          icon: const Icon(Icons.refresh),
                          label: const Text('Retry'),
                        ),
                      ],
                    ),
                  );
                }
                return widget.builder(context, ref, snapshot.data, _refresh);
              },
            ),
          ),
        ],
      ),
    ),
  );
}

class DashboardPage extends ConsumerWidget {
  const DashboardPage({super.key, this.analytics = false});
  final bool analytics;
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final admin = ref.watch(authProvider).role?.isAdministrator ?? false;
    return DataPage(
      key: ValueKey('dashboard-$admin-$analytics'),
      title: analytics
          ? 'Analytics'
          : admin
          ? 'Admin Dashboard'
          : 'Dashboard',
      load: (dio) async {
        if (admin) {
          return (await dio.get(
            analytics ? '/admin/analytics' : '/admin/dashboard',
          )).data;
        }
        final conversations = (await dio.get('/conversations/')).data as List;
        final documents = (await dio.get('/documents/list')).data as Map;
        return {
          'Conversations': conversations.length,
          'Documents': documents['total_documents'],
        };
      },
      builder: (context, ref, data, refresh) => ListView(
        children: [
          Wrap(
            spacing: 24,
            runSpacing: 24,
            children: (data as Map).entries
                .map(
                  (e) => SizedBox(
                    width: 180,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${e.value}',
                          style: Theme.of(context).textTheme.headlineMedium,
                        ),
                        Text(e.key.toString().replaceAll('_', ' ')),
                      ],
                    ),
                  ),
                )
                .toList(),
          ),
          const Divider(height: 48),
          ListTile(
            leading: const Icon(Icons.forum_outlined),
            title: const Text('Legal research'),
            trailing: const Icon(Icons.arrow_forward),
            onTap: () => context.go('/chat'),
          ),
          ListTile(
            leading: const Icon(Icons.history),
            title: const Text('Research history'),
            trailing: const Icon(Icons.arrow_forward),
            onTap: () => context.go('/history'),
          ),
          ListTile(
            leading: const Icon(Icons.description_outlined),
            title: const Text('Documents'),
            trailing: const Icon(Icons.arrow_forward),
            onTap: () => context.go('/documents'),
          ),
        ],
      ),
    );
  }
}

class HistoryPage extends StatelessWidget {
  const HistoryPage({super.key});
  @override
  Widget build(BuildContext context) => DataPage(
    title: 'Research History',
    load: (dio) async => (await dio.get('/conversations/')).data,
    builder: (context, ref, data, refresh) {
      final rows = data as List;
      if (rows.isEmpty) {
        return const Center(child: Text('No conversations yet.'));
      }
      return ListView.separated(
        itemCount: rows.length,
        separatorBuilder: (_, _) => const Divider(height: 1),
        itemBuilder: (context, index) {
          final row = rows[index] as Map;
          return ListTile(
            leading: const Icon(Icons.forum_outlined),
            title: Text(
              '${row['title']}',
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            subtitle: Text('${row['updated_at']}'.split('T').first),
            onTap: () => context.go('/chat?conversation=${row['id']}'),
            trailing: PopupMenuButton<String>(
              tooltip: 'Conversation actions',
              itemBuilder: (_) => const [
                PopupMenuItem(value: 'rename', child: Text('Rename')),
                PopupMenuItem(value: 'delete', child: Text('Delete')),
              ],
              onSelected: (action) async {
                final dio = ref.read(dioProvider);
                if (action == 'rename') {
                  final controller = TextEditingController(
                    text: '${row['title']}',
                  );
                  final title = await showDialog<String>(
                    context: context,
                    builder: (context) => AlertDialog(
                      title: const Text('Rename conversation'),
                      content: TextField(
                        controller: controller,
                        maxLength: 255,
                        autofocus: true,
                      ),
                      actions: [
                        TextButton(
                          onPressed: () => Navigator.pop(context),
                          child: const Text('Cancel'),
                        ),
                        FilledButton(
                          onPressed: () =>
                              Navigator.pop(context, controller.text.trim()),
                          child: const Text('Save'),
                        ),
                      ],
                    ),
                  );
                  if (title == null || title.isEmpty) return;
                  try {
                    await dio.patch(
                      '/conversations/${row['id']}',
                      data: {'title': title},
                    );
                    refresh();
                  } catch (e) {
                    if (context.mounted) {
                      ScaffoldMessenger.of(
                        context,
                      ).showSnackBar(SnackBar(content: Text(apiError(e))));
                    }
                  }
                } else {
                  final confirmed = await showDialog<bool>(
                    context: context,
                    builder: (context) => AlertDialog(
                      title: const Text('Delete conversation?'),
                      content: const Text(
                        'This removes its messages permanently.',
                      ),
                      actions: [
                        TextButton(
                          onPressed: () => Navigator.pop(context, false),
                          child: const Text('Cancel'),
                        ),
                        FilledButton(
                          onPressed: () => Navigator.pop(context, true),
                          child: const Text('Delete'),
                        ),
                      ],
                    ),
                  );
                  if (confirmed != true) return;
                  try {
                    await dio.delete('/conversations/${row['id']}');
                    refresh();
                  } catch (e) {
                    if (context.mounted) {
                      ScaffoldMessenger.of(
                        context,
                      ).showSnackBar(SnackBar(content: Text(apiError(e))));
                    }
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

class AccountPage extends ConsumerStatefulWidget {
  const AccountPage({super.key});
  @override
  ConsumerState<AccountPage> createState() => _AccountPageState();
}

class MonitoringPage extends StatelessWidget {
  const MonitoringPage({super.key});
  @override
  Widget build(BuildContext context) => DataPage(
    title: 'Research Monitoring',
    load: (dio) async => (await dio.get('/admin/chats')).data,
    builder: (context, ref, data, refresh) {
      final rows = data as List;
      if (rows.isEmpty) {
        return const Center(child: Text('No research activity yet.'));
      }
      return ListView.separated(
        itemCount: rows.length,
        separatorBuilder: (_, _) => const Divider(height: 1),
        itemBuilder: (context, index) {
          final row = rows[index] as Map;
          return ListTile(
            leading: const Icon(Icons.manage_search),
            title: Text(
              '${row['question']}',
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            subtitle: Text(
              '${row['user_email']} | ${row['created_at'].toString().split('T').first}',
            ),
            onTap: () => showDialog<void>(
              context: context,
              builder: (context) => AlertDialog(
                title: const Text('Research record'),
                content: SizedBox(
                  width: 600,
                  child: SingleChildScrollView(
                    child: SelectableText(
                      '${row['user_email']}\n\n${row['question']}\n\n${row['answer']}',
                    ),
                  ),
                ),
                actions: [
                  TextButton(
                    onPressed: () => Navigator.pop(context),
                    child: const Text('Close'),
                  ),
                ],
              ),
            ),
          );
        },
      );
    },
  );
}

class _AccountPageState extends ConsumerState<AccountPage> {
  final _name = TextEditingController();
  bool _busy = false;
  bool _initialized = false;
  String _language = 'English';
  String _responseStyle = 'Concise';
  @override
  void initState() {
    super.initState();
    _loadPreferences();
  }

  Future<void> _loadPreferences() async {
    try {
      final data =
          (await ref.read(dioProvider).get('/auth/preferences')).data as Map;
      if (mounted) {
        setState(() {
          _language = data['language'].toString();
          _responseStyle = data['response_style'].toString();
        });
      }
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Unable to load preferences.')),
        );
      }
    }
  }

  @override
  void dispose() {
    _name.dispose();
    super.dispose();
  }

  Future<void> _run(Future<void> Function() action, String message) async {
    setState(() => _busy = true);
    try {
      await action();
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(message)));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(apiError(e))));
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(authProvider).user;
    if (!_initialized && user != null) {
      _name.text = user.fullName ?? '';
      _initialized = true;
    }
    return Scaffold(
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          Text(
            'Account Settings',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 24),
          TextField(
            controller: _name,
            maxLength: 150,
            decoration: const InputDecoration(labelText: 'Full name'),
          ),
          const SizedBox(height: 12),
          Text(user?.email ?? ''),
          const SizedBox(height: 8),
          Text('Role: ${user?.role.displayName ?? ''}'),
          const SizedBox(height: 20),
          DropdownButtonFormField<String>(
            initialValue: _language,
            key: ValueKey(_language),
            decoration: const InputDecoration(labelText: 'Answer language'),
            items: [
              for (final value in ['English', 'Hindi', 'Marathi'])
                DropdownMenuItem(value: value, child: Text(value)),
            ],
            onChanged: _busy
                ? null
                : (value) => setState(() => _language = value!),
          ),
          const SizedBox(height: 16),
          DropdownButtonFormField<String>(
            initialValue: _responseStyle,
            key: ValueKey(_responseStyle),
            decoration: const InputDecoration(labelText: 'Answer detail'),
            items: [
              for (final value in ['Concise', 'Detailed'])
                DropdownMenuItem(value: value, child: Text(value)),
            ],
            onChanged: _busy
                ? null
                : (value) => setState(() => _responseStyle = value!),
          ),
          const SizedBox(height: 24),
          Align(
            alignment: Alignment.centerLeft,
            child: FilledButton.icon(
              icon: const Icon(Icons.save_outlined),
              label: const Text('Save profile'),
              onPressed: _busy
                  ? null
                  : () => _run(() async {
                      if (_name.text.trim().isEmpty) {
                        throw Exception('Enter your name.');
                      }
                      await ref
                          .read(dioProvider)
                          .patch(
                            '/auth/me',
                            data: {'full_name': _name.text.trim()},
                          );
                      await ref.read(authProvider.notifier).refreshProfile();
                      await ref
                          .read(dioProvider)
                          .put(
                            '/auth/preferences',
                            data: {
                              'language': _language,
                              'response_style': _responseStyle,
                            },
                          );
                    }, 'Profile updated.'),
            ),
          ),
          const Divider(height: 40),
          ListTile(
            leading: const Icon(Icons.lock_reset),
            title: const Text('Reset password'),
            onTap: _busy || user == null
                ? null
                : () => _run(
                    () => ref
                        .read(firebaseAuthServiceProvider)
                        .sendPasswordResetEmail(user.email),
                    'Password reset email sent.',
                  ),
          ),
          ListTile(
            leading: const Icon(Icons.logout),
            title: const Text('Sign out'),
            onTap: _busy
                ? null
                : () async {
                    await ref.read(authProvider.notifier).logout();
                    if (context.mounted) context.go('/login');
                  },
          ),
        ],
      ),
    );
  }
}
