import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../chat/providers/chat_providers.dart';
import '../../chat/domain/models/chat_models.dart';
import 'workspace_pages.dart';

class DocumentAnalysisPage extends ConsumerStatefulWidget {
  const DocumentAnalysisPage({
    super.key,
    this.compare = false,
    this.initialDocument,
  });
  final bool compare;
  final String? initialDocument;
  @override
  ConsumerState<DocumentAnalysisPage> createState() =>
      _DocumentAnalysisPageState();
}

class _DocumentAnalysisPageState extends ConsumerState<DocumentAnalysisPage> {
  List<dynamic> _documents = [];
  final Set<String> _selected = {};
  final _focus = TextEditingController();
  bool _loading = true;
  bool _running = false;
  String? _error;
  ChatMessage? _answer;
  @override
  void initState() {
    super.initState();
    if (widget.initialDocument != null) _selected.add(widget.initialDocument!);
    _load();
  }

  @override
  void dispose() {
    _focus.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    try {
      final data =
          (await ref.read(dioProvider).get('/documents/list')).data as Map;
      if (!mounted) return;
      setState(() {
        _documents = (data['documents'] as List)
            .where((d) => d['status'] == 'completed')
            .toList();
        _loading = false;
        _error = null;
      });
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = apiError(e);
          _loading = false;
        });
      }
    }
  }

  Future<void> _analyze() async {
    setState(() {
      _running = true;
      _error = null;
      _answer = null;
    });
    final question = widget.compare
        ? 'Compare the selected documents. Identify material clause differences, obligations, termination terms, dates, and risks. Cite document names and pages for every finding. ${_focus.text.trim()}'
        : 'Summarize the selected document. Cover parties, purpose, obligations, payments, deadlines, termination, and important clauses. Cite document names and pages. ${_focus.text.trim()}';
    try {
      final data =
          (await ref
                      .read(dioProvider)
                      .post(
                        '/chat/',
                        data: FormData.fromMap({
                          'question': question,
                          'document_ids': jsonEncode(_selected.toList()),
                        }),
                      ))
                  .data
              as Map;
      if (!mounted) return;
      setState(
        () => _answer = ChatMessage(
          id: data['chat_id'].toString(),
          content: data['answer'].toString(),
          role: MessageRole.assistant,
          createdAt: DateTime.now(),
          citations: ((data['citations'] as List?) ?? [])
              .map(
                (c) => ChatCitation(
                  filename: c['filename'].toString(),
                  page: (c['page'] as num).toInt(),
                ),
              )
              .toList(),
        ),
      );
    } catch (e) {
      if (mounted) setState(() => _error = apiError(e));
    } finally {
      if (mounted) setState(() => _running = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    body: ListView(
      padding: const EdgeInsets.all(24),
      children: [
        Text(
          widget.compare ? 'Compare Documents' : 'Document Summary',
          style: Theme.of(context).textTheme.headlineSmall,
        ),
        const SizedBox(height: 20),
        if (_loading)
          const Center(child: CircularProgressIndicator())
        else if (_documents.isEmpty)
          ListTile(
            title: const Text('No processed documents yet.'),
            trailing: IconButton(
              tooltip: 'Refresh documents',
              onPressed: _load,
              icon: const Icon(Icons.refresh),
            ),
          )
        else ...[
          for (final doc in _documents)
            CheckboxListTile(
              title: Text(
                '${doc['filename']}',
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              value: _selected.contains(doc['id'].toString()),
              onChanged: _running
                  ? null
                  : (checked) => setState(() {
                      final id = doc['id'].toString();
                      if (checked == true) {
                        if (!widget.compare) _selected.clear();
                        if (_selected.length < 10) _selected.add(id);
                      } else {
                        _selected.remove(id);
                      }
                    }),
            ),
          const SizedBox(height: 16),
          TextField(
            controller: _focus,
            maxLength: 1000,
            decoration: const InputDecoration(
              labelText: 'Focus or specific clauses (optional)',
            ),
          ),
          const SizedBox(height: 16),
          Align(
            alignment: Alignment.centerLeft,
            child: FilledButton.icon(
              onPressed: _running || _selected.length < (widget.compare ? 2 : 1)
                  ? null
                  : _analyze,
              icon: const Icon(Icons.auto_awesome_outlined),
              label: Text(widget.compare ? 'Compare' : 'Generate summary'),
            ),
          ),
        ],
        if (_running)
          const Padding(
            padding: EdgeInsets.all(24),
            child: Center(child: CircularProgressIndicator()),
          ),
        if (_error != null)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 16),
            child: Text(_error!),
          ),
        if (_answer != null) ...[
          const Divider(height: 40),
          Align(
            alignment: Alignment.centerRight,
            child: IconButton(
              tooltip: 'Copy answer',
              icon: const Icon(Icons.copy_outlined),
              onPressed: () =>
                  Clipboard.setData(ClipboardData(text: _answer!.content)),
            ),
          ),
          MarkdownBody(data: _answer!.content, selectable: true),
          const SizedBox(height: 16),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              for (final citation in _answer!.citations)
                ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 280),
                  child: Chip(
                    avatar: const Icon(Icons.description_outlined, size: 16),
                    label: Text(
                      '${citation.filename}, p. ${citation.page}',
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ),
            ],
          ),
        ],
      ],
    ),
  );
}
