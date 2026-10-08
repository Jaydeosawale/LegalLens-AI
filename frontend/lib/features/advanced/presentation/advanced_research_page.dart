import 'package:flutter/material.dart';

import 'package:go_router/go_router.dart';

class AdvancedResearchPage extends StatefulWidget {
  const AdvancedResearchPage({super.key});
  @override
  State<AdvancedResearchPage> createState() => _AdvancedResearchPageState();
}

class _AdvancedResearchPageState extends State<AdvancedResearchPage> {
  final _question = TextEditingController();
  String _mode = 'Research';
  @override
  void dispose() {
    _question.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          Text(
            'Advanced Research',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 24),
          SegmentedButton<String>(
            segments: const [
              ButtonSegment(
                value: 'Research',
                label: Text('Research'),
                icon: Icon(Icons.search),
              ),
              ButtonSegment(
                value: 'Compare',
                label: Text('Compare'),
                icon: Icon(Icons.compare_arrows),
              ),
              ButtonSegment(
                value: 'Summarize',
                label: Text('Summary'),
                icon: Icon(Icons.subject),
              ),
            ],
            selected: {_mode},
            onSelectionChanged: (value) => setState(() => _mode = value.first),
          ),
          const SizedBox(height: 24),
          TextField(
            controller: _question,
            minLines: 5,
            maxLines: 12,
            maxLength: 8000,
            decoration: const InputDecoration(
              labelText: 'Research question',
              alignLabelWithHint: true,
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 16),
          Align(
            alignment: Alignment.centerLeft,
            child: FilledButton.icon(
              icon: const Icon(Icons.search),
              label: const Text('Start research'),
              onPressed: () {
                if (_question.text.trim().isEmpty) return;
                final prefix = switch (_mode) {
                  'Compare' =>
                    'Compare the relevant legal provisions, explaining similarities and differences with citations: ',
                  'Summarize' =>
                    'Summarize the relevant legal provisions and cite sources: ',
                  _ =>
                    'Research the following question using the available documents with citations: ',
                };
                context.go(
                  Uri(
                    path: '/chat',
                    queryParameters: {
                      'question': '$prefix${_question.text.trim()}',
                    },
                  ).toString(),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
