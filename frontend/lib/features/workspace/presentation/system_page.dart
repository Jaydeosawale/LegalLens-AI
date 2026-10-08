import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../chat/providers/chat_providers.dart';
import 'workspace_pages.dart';
import '../../auth/providers/auth_provider.dart';
import '../../../core/auth/user_role.dart';

class SystemPage extends ConsumerStatefulWidget {
  const SystemPage({super.key});
  @override
  ConsumerState<SystemPage> createState() => _SystemPageState();
}

class _SystemPageState extends ConsumerState<SystemPage> {
  final _model = TextEditingController();
  final _dailyLimit = TextEditingController();
  bool _savingLimit = false;
  double _temperature = 0;
  int _topK = 8;
  bool _saving = false;
  bool _initialized = false;
  @override
  void dispose() {
    _model.dispose();
    _dailyLimit.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => DataPage(
    title: 'System Configuration',
    load: (dio) async => (await dio.get('/admin/system')).data,
    builder: (context, ref, data, refresh) {
      final settings = data['settings'] as Map;
      if (!_initialized) {
        _model.text = settings['model_name'].toString();
        _temperature = (settings['temperature'] as num).toDouble();
        _topK = (settings['top_k'] as num).toInt();
        _dailyLimit.text =
            '${data['chat_limits']?['normal_user_daily_messages'] ?? 10}';
        _initialized = true;
      }
      final health = data['health'] as Map;
      final events = data['events'] as List;
      return ListView(
        children: [
          Text('System Health', style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 12),
          Wrap(
            spacing: 24,
            runSpacing: 16,
            children: health.entries
                .map(
                  (e) => SizedBox(
                    width: 160,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(e.key.toString().replaceAll('_', ' ')),
                        Text(
                          '${e.value}',
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                      ],
                    ),
                  ),
                )
                .toList(),
          ),
          const Divider(height: 40),
          if (ref.watch(authProvider).user?.role == UserRole.superAdmin) ...[
            Text('Chat Limits', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 16),
            SizedBox(
              width: 280,
              child: TextField(
                controller: _dailyLimit,
                enabled: !_savingLimit,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Daily messages per normal user',
                ),
              ),
            ),
            const SizedBox(height: 16),
            Align(
              alignment: Alignment.centerLeft,
              child: FilledButton.icon(
                icon: const Icon(Icons.save_outlined),
                label: const Text('Save chat limit'),
                onPressed: _savingLimit
                    ? null
                    : () async {
                        final limit = int.tryParse(_dailyLimit.text.trim());
                        if (limit == null || limit < 10 || limit > 1000) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text(
                                'Enter a whole number from 10 to 1000.',
                              ),
                            ),
                          );
                          return;
                        }
                        setState(() => _savingLimit = true);
                        try {
                          await ref
                              .read(dioProvider)
                              .put(
                                '/admin/system/chat-limits',
                                data: {'normal_user_daily_messages': limit},
                              );
                          if (context.mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Daily chat limit saved.'),
                              ),
                            );
                            refresh();
                          }
                        } catch (e) {
                          if (context.mounted)
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(content: Text(apiError(e))),
                            );
                        } finally {
                          if (mounted) setState(() => _savingLimit = false);
                        }
                      },
              ),
            ),
            const Divider(height: 40),
          ],
          Text('AI Model', style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 16),
          TextField(
            controller: _model,
            maxLength: 100,
            decoration: const InputDecoration(labelText: 'Groq model ID'),
          ),
          Text('Temperature: ${_temperature.toStringAsFixed(1)}'),
          Slider(
            value: _temperature,
            min: 0,
            max: 1,
            divisions: 10,
            label: _temperature.toStringAsFixed(1),
            onChanged: _saving
                ? null
                : (value) => setState(() => _temperature = value),
          ),
          Row(
            children: [
              const Expanded(child: Text('Retrieved source chunks')),
              IconButton(
                tooltip: 'Fewer chunks',
                onPressed: _saving || _topK <= 2
                    ? null
                    : () => setState(() => _topK--),
                icon: const Icon(Icons.remove),
              ),
              SizedBox(
                width: 32,
                child: Text('$_topK', textAlign: TextAlign.center),
              ),
              IconButton(
                tooltip: 'More chunks',
                onPressed: _saving || _topK >= 20
                    ? null
                    : () => setState(() => _topK++),
                icon: const Icon(Icons.add),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Align(
            alignment: Alignment.centerLeft,
            child: FilledButton.icon(
              icon: const Icon(Icons.save_outlined),
              label: const Text('Save configuration'),
              onPressed: _saving
                  ? null
                  : () async {
                      setState(() => _saving = true);
                      try {
                        await ref
                            .read(dioProvider)
                            .put(
                              '/admin/system/settings',
                              data: {
                                'model_name': _model.text.trim(),
                                'temperature': _temperature,
                                'top_k': _topK,
                              },
                            );
                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('Configuration saved.'),
                            ),
                          );
                          refresh();
                        }
                      } catch (e) {
                        if (context.mounted) {
                          ScaffoldMessenger.of(
                            context,
                          ).showSnackBar(SnackBar(content: Text(apiError(e))));
                        }
                      } finally {
                        if (mounted) setState(() => _saving = false);
                      }
                    },
            ),
          ),
          const Divider(height: 40),
          Text(
            'System Activity',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          if (events.isEmpty)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 16),
              child: Text('No configuration changes yet.'),
            ),
          for (final event in events)
            ListTile(
              leading: const Icon(Icons.receipt_long_outlined),
              title: Text('${event['action']}'),
              subtitle: Text('${event['actor']}\n${event['created_at']}'),
            ),
        ],
      );
    },
  );
}
