import 'package:dio/dio.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../workspace/presentation/workspace_pages.dart';
import '../../chat/providers/chat_providers.dart';
import '../../auth/providers/auth_provider.dart';
import '../../../core/auth/user_role.dart';

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
  String _reviewFilter = 'all';

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
              : 'Document uploaded. Approval is required before RAG use.',
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

  Future<void> _manageDocument(
    String action,
    Map<String, dynamic> document,
  ) async {
    final dio = ref.read(dioProvider);
    final id = document['id'];
    try {
      if (action == 'access') {
        await dio.patch(
          '/documents/$id/access',
          data: {'enabled': document['access_enabled'] != true},
        );
      } else if (action == 'submit') {
        final confirmed = await showDialog<bool>(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Submit for review?'),
            content: const Text(
              'RAG use will remain unavailable until the super admin approves this document.',
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('Cancel'),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(context, true),
                child: const Text('Submit'),
              ),
            ],
          ),
        );
        if (confirmed != true) return;
        await dio.post('/documents/$id/submit');
      } else {
        var shared = false;
        var note = '';
        final canShare = [
          'admin',
          'super_admin',
        ].contains(document['owner_role']);
        final confirmed = await showDialog<bool>(
          context: context,
          builder: (context) => StatefulBuilder(
            builder: (context, setDialogState) => AlertDialog(
              title: Text(
                action == 'approved' ? 'Approve document?' : 'Reject document?',
              ),
              content: SizedBox(
                width: 420,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    if (action == 'approved' && canShare)
                      SwitchListTile(
                        contentPadding: EdgeInsets.zero,
                        title: const Text('Shared knowledge base'),
                        value: shared,
                        onChanged: (value) =>
                            setDialogState(() => shared = value),
                      ),
                    TextField(
                      maxLength: 1000,
                      maxLines: 3,
                      decoration: const InputDecoration(
                        labelText: 'Review note',
                      ),
                      onChanged: (value) => note = value,
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context, false),
                  child: const Text('Cancel'),
                ),
                FilledButton(
                  onPressed: () => Navigator.pop(context, true),
                  child: Text(
                    action == 'approved' ? 'Approve and index' : 'Reject',
                  ),
                ),
              ],
            ),
          ),
        );
        if (confirmed != true) return;
        await dio.post(
          '/documents/$id/review',
          data: {
            'decision': action,
            'scope': shared ? 'shared' : 'private',
            'note': note,
          },
        );
      }
      if (mounted) await _loadDocuments();
    } catch (error) {
      if (mounted) _showMessage(apiError(error));
    }
  }

  @override
  Widget build(BuildContext context) {
    const canUpload = true;
    final role = ref.watch(authProvider).role ?? UserRole.user;
    final visible = _documents
        .where(
          (d) =>
              (_reviewFilter == 'all' ||
                  d['approval_status'] == _reviewFilter) &&
              d['filename'].toString().toLowerCase().contains(
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
                DropdownButtonFormField<String>(
                  initialValue: _reviewFilter,
                  decoration: const InputDecoration(labelText: 'Review status'),
                  items: const [
                    DropdownMenuItem(
                      value: 'all',
                      child: Text('All documents'),
                    ),
                    DropdownMenuItem(
                      value: 'draft',
                      child: Text('Awaiting admin submission'),
                    ),
                    DropdownMenuItem(
                      value: 'pending',
                      child: Text('Pending super-admin review'),
                    ),
                    DropdownMenuItem(
                      value: 'approved',
                      child: Text('Approved'),
                    ),
                    DropdownMenuItem(
                      value: 'rejected',
                      child: Text('Rejected'),
                    ),
                  ],
                  onChanged: (value) =>
                      setState(() => _reviewFilter = value ?? 'all'),
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
                            '${document['approval_status'] ?? 'draft'} | ${document['rag_scope'] ?? 'private'} | ${document['access_enabled'] == false ? 'Access disabled' : 'Access enabled'}${size == null ? '' : ' | ${(size / 1024).toStringAsFixed(0)} KB'}',
                          ),
                          onTap: () => showDialog<void>(
                            context: context,
                            builder: (context) => AlertDialog(
                              title: Text(name),
                              content: Text(
                                'Processing: ${document['status']}\nReview: ${document['approval_status']}\nScope: ${document['rag_scope']}\nReview note: ${document['review_note'] ?? '-'}\nSize: ${size == null ? '-' : '${(size / 1024).round()} KB'}\nUploaded: ${document['created_at'].toString().split('T').first}',
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
                            itemBuilder: (_) => [
                              if (document['approval_status'] == 'approved' &&
                                  document['access_enabled'] != false)
                                const PopupMenuItem(
                                  value: 'summary',
                                  child: Text('Summarize'),
                                ),
                              if (role.isAdministrator) ...[
                                if (document['approval_status'] != 'pending')
                                  const PopupMenuItem(
                                    value: 'submit',
                                    child: Text('Submit for review'),
                                  ),
                                if (role == UserRole.superAdmin &&
                                    document['approval_status'] ==
                                        'pending') ...[
                                  const PopupMenuItem(
                                    value: 'approved',
                                    child: Text('Approve and index'),
                                  ),
                                  const PopupMenuItem(
                                    value: 'rejected',
                                    child: Text('Reject'),
                                  ),
                                ],
                                PopupMenuItem(
                                  value: 'access',
                                  child: Text(
                                    document['access_enabled'] == false
                                        ? 'Enable access'
                                        : 'Disable access',
                                  ),
                                ),
                              ],
                              const PopupMenuItem(
                                value: 'delete',
                                child: Text('Delete'),
                              ),
                            ],
                            onSelected: (action) async {
                              if ([
                                'submit',
                                'approved',
                                'rejected',
                                'access',
                              ].contains(action)) {
                                await _manageDocument(action, document);
                                return;
                              }
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
