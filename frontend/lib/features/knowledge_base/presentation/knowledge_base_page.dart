import 'package:dio/dio.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../workspace/presentation/workspace_pages.dart';
import '../../chat/providers/chat_providers.dart';

class KnowledgeBasePage extends ConsumerStatefulWidget {
  const KnowledgeBasePage({super.key});

  @override
  ConsumerState<KnowledgeBasePage> createState() => _KnowledgeBasePageState();
}

class _KnowledgeBasePageState extends ConsumerState<KnowledgeBasePage> {
  static const maxFileBytes = 10 * 1024 * 1024;

  List<Map<String, dynamic>> _documents = [];
  bool _loading = true;
  bool _uploading = false;
  String? _error;
  String _search = '';

  @override
  void initState() {
    super.initState();
    Future.microtask(_loadDocuments);
  }

  Future<void> _loadDocuments() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final response = await ref
          .read(dioProvider)
          .get<Map<String, dynamic>>('/documents/list');
      final documents = response.data?['documents'] as List<dynamic>? ?? [];
      if (!mounted) return;
      setState(() {
        _documents = documents.cast<Map<String, dynamic>>();
        _loading = false;
      });
    } on DioException catch (error) {
      if (!mounted) return;
      setState(() {
        _error = error.response?.statusCode == 401
            ? 'Sign in to view documents.'
            : 'Unable to load documents. Please try again.';
        _loading = false;
      });
    }
  }

  Future<void> _uploadDocument() async {
    final file = await FilePicker.pickFile(
      type: FileType.custom,
      allowedExtensions: ['pdf'],
    );
    if (file == null || !mounted) return;

    final size = await file.length();
    if (size == null || size == 0 || size > maxFileBytes) {
      _showMessage('Choose a PDF that is 10 MB or smaller.');
      return;
    }
    final bytes = await file.readAsBytes();

    setState(() => _uploading = true);
    try {
      final response = await ref
          .read(dioProvider)
          .post<Map<String, dynamic>>(
            '/documents/upload',
            data: FormData.fromMap({
              'files': MultipartFile.fromBytes(bytes, filename: file.name),
            }),
          );
      if (!mounted) return;
      final data = response.data ?? {};
      if (data['success'] != true) {
        final results = data['results'] as List<dynamic>? ?? [];
        final detail = results.isNotEmpty
            ? (results.first as Map<String, dynamic>)['error']?.toString()
            : null;
        _showMessage(detail ?? 'Document processing failed.');
      } else {
        _showMessage(
          data['duplicates'] == 1
              ? 'This PDF is already in the knowledge base.'
              : 'Document added to the knowledge base.',
        );
        await _loadDocuments();
      }
    } on DioException catch (error) {
      if (!mounted) return;
      _showMessage(
        error.response?.statusCode == 403
            ? 'Document upload requires administrator access.'
            : 'Upload failed. Please try again.',
      );
    } finally {
      if (mounted) setState(() => _uploading = false);
    }
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    const canUpload = true;
    final visible = _documents
        .where(
          (d) => d['filename'].toString().toLowerCase().contains(
            _search.toLowerCase(),
          ),
        )
        .toList();

    return Scaffold(
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 920),
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        'Documents',
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                    ),
                    IconButton(
                      tooltip: 'Refresh documents',
                      onPressed: _loading ? null : _loadDocuments,
                      icon: const Icon(Icons.refresh),
                    ),
                    if (canUpload) ...[
                      const SizedBox(width: 8),
                      FilledButton.icon(
                        onPressed: _uploading ? null : _uploadDocument,
                        icon: _uploading
                            ? const SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                ),
                              )
                            : const Icon(Icons.upload_file_outlined),
                        label: const Text('Upload PDF'),
                      ),
                    ],
                  ],
                ),
                const SizedBox(height: 20),
                TextField(
                  decoration: const InputDecoration(
                    labelText: 'Search documents',
                    prefixIcon: Icon(Icons.search),
                  ),
                  onChanged: (value) => setState(() => _search = value),
                ),
                const SizedBox(height: 16),
                if (_loading)
                  const Expanded(
                    child: Center(child: CircularProgressIndicator()),
                  )
                else if (_error != null)
                  Expanded(child: Center(child: Text(_error!)))
                else if (_documents.isEmpty)
                  const Expanded(
                    child: Center(child: Text('No documents yet.')),
                  )
                else
                  Expanded(
                    child: ListView.separated(
                      itemCount: visible.length,
                      separatorBuilder: (_, _) => const Divider(height: 1),
                      itemBuilder: (context, index) {
                        final document = visible[index];
                        final name =
                            document['filename']?.toString() ??
                            'Untitled document';
                        final size = document['file_size'] as num?;
                        return ListTile(
                          leading: const Icon(Icons.picture_as_pdf_outlined),
                          title: Text(name, overflow: TextOverflow.ellipsis),
                          subtitle: Text(
                            size == null
                                ? 'PDF'
                                : '${(size / 1024).toStringAsFixed(0)} KB',
                          ),
                          onTap: () => showDialog<void>(
                            context: context,
                            builder: (context) => AlertDialog(
                              title: Text(name),
                              content: Text(
                                'Status: ${document['status']}\nSize: ${size == null ? '-' : '${(size / 1024).round()} KB'}\nUploaded: ${document['created_at'].toString().split('T').first}',
                              ),
                              actions: [
                                TextButton(
                                  onPressed: () => Navigator.pop(context),
                                  child: const Text('Close'),
                                ),
                              ],
                            ),
                          ),
                          trailing: PopupMenuButton<String>(
                            tooltip: 'Document actions',
                            itemBuilder: (_) => const [
                              PopupMenuItem(
                                value: 'summary',
                                child: Text('Summarize'),
                              ),
                              PopupMenuItem(
                                value: 'delete',
                                child: Text('Delete'),
                              ),
                            ],
                            onSelected: (action) async {
                              if (action == 'summary') {
                                context.go(
                                  '/summary?document=${document['id']}',
                                );
                                return;
                              }
                              final approved = await showDialog<bool>(
                                context: context,
                                builder: (context) => AlertDialog(
                                  title: const Text('Delete document?'),
                                  content: Text(
                                    'Remove $name and its searchable content?',
                                  ),
                                  actions: [
                                    TextButton(
                                      onPressed: () =>
                                          Navigator.pop(context, false),
                                      child: const Text('Cancel'),
                                    ),
                                    FilledButton(
                                      onPressed: () =>
                                          Navigator.pop(context, true),
                                      child: const Text('Delete'),
                                    ),
                                  ],
                                ),
                              );
                              if (approved != true) return;
                              try {
                                await ref
                                    .read(dioProvider)
                                    .delete('/documents/${document['id']}');
                                await _loadDocuments();
                              } catch (e) {
                                if (mounted) _showMessage(apiError(e));
                              }
                            },
                          ),
                        );
                      },
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
