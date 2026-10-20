import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../features/chat/providers/chat_providers.dart';

const legalResearchNotice =
    'AI research assistance, not legal advice. Verify answers and citations with official sources and a qualified lawyer. Questions and relevant document excerpts are sent to Groq. Avoid confidential or sensitive personal information.';

class PolicyLinks extends StatelessWidget {
  const PolicyLinks({super.key});
  Future<void> _open(BuildContext context, String slug) async {
    final ok = await launchUrl(
      Uri.parse(
        'https://jaydeo-sawale-portfolio.vercel.app/legallens-ai/$slug/',
      ),
      mode: LaunchMode.externalApplication,
    );
    if (!ok && context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Unable to open page. Contact jaydeep.sawale97@gmail.com.',
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) => Column(
    children: [
      ListTile(
        leading: const Icon(Icons.privacy_tip_outlined),
        title: const Text('Privacy policy'),
        onTap: () => _open(context, 'privacy'),
      ),
      ListTile(
        leading: const Icon(Icons.person_remove_outlined),
        title: const Text('Request account and data deletion'),
        subtitle: const Text('Opens deletion instructions and support contact'),
        onTap: () => _open(context, 'delete-account'),
      ),
    ],
  );
}

class ReportAiAnswer extends ConsumerWidget {
  const ReportAiAnswer({super.key, required this.content});
  final String content;
  @override
  Widget build(BuildContext context, WidgetRef ref) => TextButton.icon(
    icon: const Icon(Icons.flag_outlined, size: 18),
    label: const Text('Report AI answer'),
    onPressed: () => showDialog<void>(
      context: context,
      builder: (_) => _ReportDialog(content: content),
    ),
  );
}

class _ReportDialog extends ConsumerStatefulWidget {
  const _ReportDialog({required this.content});
  final String content;
  @override
  ConsumerState<_ReportDialog> createState() => _ReportDialogState();
}

class _ReportDialogState extends ConsumerState<_ReportDialog> {
  final details = TextEditingController();
  String reason = 'Incorrect or misleading';
  bool busy = false;
  String? error;
  @override
  void dispose() {
    details.dispose();
    super.dispose();
  }

  Future<void> submit() async {
    setState(() {
      busy = true;
      error = null;
    });
    try {
      await ref
          .read(dioProvider)
          .post(
            '/content-reports',
            data: {
              'reason': reason,
              'content': widget.content.length > 8000
                  ? widget.content.substring(0, 8000)
                  : widget.content,
              'details': details.text.trim(),
            },
          );
      if (mounted) {
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Report submitted for review. Thank you.'),
          ),
        );
      }
    } catch (_) {
      if (mounted) {
        setState(() {
          error = 'Report could not be sent. Try again or contact support.';
          busy = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) => AlertDialog(
    title: const Text('Report AI answer'),
    content: SizedBox(
      width: 440,
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'The selected answer and your details will be sent to LegalLens for review. Do not include private information.',
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              initialValue: reason,
              isExpanded: true,
              items: [
                for (final value in [
                  'Harmful or unsafe',
                  'Incorrect or misleading',
                  'Privacy concern',
                  'Other',
                ])
                  DropdownMenuItem(value: value, child: Text(value)),
              ],
              onChanged: busy ? null : (v) => setState(() => reason = v!),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: details,
              enabled: !busy,
              maxLength: 1000,
              maxLines: 3,
              decoration: const InputDecoration(
                labelText: 'Details (optional)',
              ),
            ),
            if (error != null)
              Text(
                error!,
                style: TextStyle(color: Theme.of(context).colorScheme.error),
              ),
          ],
        ),
      ),
    ),
    actions: [
      TextButton(
        onPressed: busy ? null : () => Navigator.pop(context),
        child: const Text('Cancel'),
      ),
      FilledButton(
        onPressed: busy ? null : submit,
        child: Text(busy ? 'Sending…' : 'Submit report'),
      ),
    ],
  );
}
